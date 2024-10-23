from faker import Faker
from PIL import Image, ImageDraw

from datetime import datetime, UTC
import hashlib

from dor.settings import S, text_font, template_env

from .parts import FileUses, Md, MdGrp, File, FileGrp, calculate_checksum, generate_md5
from .premis import build_event

IMAGE_WIDTH = 680
IMAGE_HEIGHT = 1024

IMAGE_COLORS = {
    FileUses.access: {"background": "#eeeeee", "text": "#666666"},
    FileUses.source: {"background": "#666666", "text": "#eeeeee"},
}

def build_image(use, seq, version):
    background_color = IMAGE_COLORS[use]["background"]
    text_color = IMAGE_COLORS[use]["text"]

    image = Image.new("RGB", (IMAGE_WIDTH, IMAGE_HEIGHT), color=background_color)
    d = ImageDraw.Draw(image)

    message = f"Page v{version}.{seq}"

    _, _, w, h = d.textbbox((0, 0), message, font=text_font)
    d.text(
        ((IMAGE_WIDTH - w) / 2, (IMAGE_HEIGHT - h) / 2),
        message,
        font=text_font,
        fill=text_color,
    )

    return image


def build_plaintext(use, seq, version):
    fake = Faker(["it_IT", "en_US", "ja_JP"])
    buffer = [f"Page v{version}.{seq}"]
    buffer.append(fake["en_US"].paragraph(nb_sentences=5))
    buffer.append(fake["it_IT"].paragraph(nb_sentences=5))
    buffer.append(fake["ja_JP"].paragraph(nb_sentences=5))

    return "\n\n".join(buffer)


def build_asset(seq, object_pathname, version):
    padded_seq = f"{seq:08d}"
    # local_identifier = generate_uuid()
    local_identifier = hashlib.md5(padded_seq.encode('utf-8')).hexdigest()
    identifier = f"urn:umich.edu:dor:asset:{local_identifier}"

    mix_template = template_env.get_template("metadata_mix.xml")
    textmd_template = template_env.get_template("metadata_textmd.xml")
    asset_template = template_env.get_template("mets_asset.xml")

    md_group = MdGrp(use="TECHNICAL")
    file_group = FileGrp(use="CONTENTS")

    metadata = {}
    metadata["format_name"] = "image/jpeg"
    metadata["height"] = IMAGE_HEIGHT
    metadata["width"] = IMAGE_WIDTH
    metadata["collid"] = S.collid

    padded_seq = f"{seq:08d}"

    # access
    image = build_image(use=FileUses.access, seq=seq, version=version)
    image_filename = f"{padded_seq}.access.jpg"

    metadata["object_identifier"] = f"{identifier}:{image_filename}"
    image_pathname = object_pathname.joinpath("data", image_filename)
    metadata_pathname = object_pathname.joinpath("metadata", f"{image_filename}.mix.xml")
    image.save(image_pathname)
    metadata_pathname.open("w").write(
        mix_template.render(**metadata)
    )

    md_group.items.append(
        Md(
            use="TECHNICAL",
            mdtype="MIX",
            locref=f"../metadata/{image_filename}.mix.xml",
            checksum=calculate_checksum(metadata_pathname),
        )
    )

    file = File(
        id=generate_md5(image_filename),
        use=str(FileUses.access.value),
        mdid=md_group.items[-1].id,
        locref=f"../data/{image_filename}",
        mimetype="image/jpeg",
        checksum=calculate_checksum(image_pathname)
    )
    file_group.files.append(file)

    premis_event = build_event(event_type='generate access derivative', linking_agent_type='image processing')
    premis_event['object_identifier'] = file.id

    # source
    image = build_image(use=FileUses.source, seq=seq, version=version)
    image_filename = f"{padded_seq}.source.jpg"
    metadata["object_identifier"] = f"{identifier}:{image_filename}"
    image_pathname = object_pathname.joinpath("data", image_filename)
    metadata_pathname = object_pathname.joinpath(
        "metadata", f"{image_filename}.mix.xml"
    )
    image.save(image_pathname)
    metadata_pathname.open("w").write(mix_template.render(**metadata))

    md_group.items.append(
        Md(
            use="TECHNICAL",
            mdtype="NISOIMG",
            locref=f"../metadata/{image_filename}.mix.xml",
            checksum=calculate_checksum(metadata_pathname)
        )
    )

    metadata["object_identifier"] = f"{identifier}:{image_filename}"
    object_pathname.joinpath("metadata", f"{image_filename}.mix.xml").open("w").write(
        mix_template.render(**metadata)
    )
    file = File(
        id=generate_md5(image_filename),
        use=str(FileUses.source.value),
        mdid=md_group.items[-1].id,
        locref=f"../data/{image_filename}",
        mimetype="image/jpeg",
        checksum=calculate_checksum(image_pathname),
    )
    file_group.files.append(file)

    plaintext = build_plaintext(use=FileUses.source, seq=seq, version=version)
    text_filename = f"{padded_seq}.plaintext.txt"
    text_pathname = object_pathname.joinpath("data", text_filename)
    metadata_pathname = object_pathname.joinpath("metadata", f"{text_filename}.textmd.xml")

    text_pathname.open("w").write(plaintext)
    metadata_pathname.open("w").write(
        textmd_template.render(**metadata)
    )

    md_group.items.append(
        Md(
            use="TECHNICAL",
            mdtype="TEXTMD",
            locref=f"../metadata/{text_filename}.textmd.xml",
            checksum=calculate_checksum(metadata_pathname),
        )
    )

    file = File(
        id=generate_md5(text_filename),
        use=str(FileUses.source.value),
        mdid=md_group.items[-1].id,
        locref=f"../data/{text_filename}",
        mimetype="text/plain",
        checksum=calculate_checksum(text_pathname),
    )
    file_group.files.append(file)

    object_pathname.joinpath("descriptor", local_identifier + ".mets2.xml").open("w").write(
        asset_template.render(
            object_identifier=identifier,
            file_group=file_group, 
            md_group=md_group,
            seq=seq,
            action=S.action.value,
            event=premis_event,
            create_date=datetime.now(tz=UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
        )
    )

    return local_identifier