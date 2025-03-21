from faker import Faker
from PIL import Image, ImageDraw

from datetime import datetime, UTC
import hashlib

from dor.settings import S, text_font, template_env

from .parts import (
    UseFormats,
    UseFunctions,
    Identifier,
    Md,
    File,
    FileGrp,
    IdGenerator,
    calculate_checksum,
    generate_md5,
    generate_uuid,
    make_paths,
    get_faker,
    get_datetime,
    flatten_use,
)
from .premis import build_event

IMAGE_WIDTH = 680
IMAGE_HEIGHT = 1024

IMAGE_COLORS = {
    UseFunctions.service: {"background": "#eeeeee", "text": "#666666"},
    UseFunctions.source: {"background": "#666666", "text": "#eeeeee"},
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
    fake = get_faker(role='plaintext')

    buffer = [f"Page v{version}.{seq}"]
    buffer.append(fake["en_US"].paragraph(nb_sentences=5))
    buffer.append(fake["it_IT"].paragraph(nb_sentences=5))
    buffer.append(fake["ja_JP"].paragraph(nb_sentences=5))

    return "\n\n".join(buffer)


def build_file_set(item_identifier, seq, package_pathname, version):
    local_identifier = generate_uuid(base=16*16*16*item_identifier.start+seq)
    identifier = local_identifier

    file_set_pathname = make_paths(package_pathname.joinpath(str(identifier)))

    id_generator = IdGenerator(
        Identifier(start=16 * 16 * 16 * item_identifier.start + seq, collid=item_identifier.collid)
    )

    mix_template = template_env.get_template("metadata_mix.xml")
    textmd_template = template_env.get_template("metadata_textmd.xml")
    file_set_template = template_env.get_template("mets_file_set.xml")
    premis_event_template = template_env.get_template("premis_event.xml")

    mdsec_items = []
    file_group = FileGrp(use="CONTENTS")

    metadata = {}
    metadata["format_name"] = "image/jpeg"
    metadata["height"] = IMAGE_HEIGHT
    metadata["width"] = IMAGE_WIDTH
    metadata["collid"] = S.collid

    padded_seq = f"{seq:08d}"

    # source
    image = build_image(use=UseFunctions.source, seq=seq, version=version)
    image_filename = f"{padded_seq}.source.jpg"
    metadata["object_identifier"] = f"{identifier}:{image_filename}"
    image_pathname = file_set_pathname.joinpath("data", image_filename)
    metadata_pathname = file_set_pathname.joinpath(
        "metadata", f"{image_filename}.mix.xml"
    )
    image.save(image_pathname)
    metadata_pathname.open("w").write(mix_template.render(**metadata))

    mdsec_items.append(
        Md(
            id=id_generator(),
            use=flatten_use(UseFunctions.technical),
            mdtype="NISOIMG",
            locref=f"{identifier}/metadata/{image_filename}.mix.xml",
            checksum=calculate_checksum(metadata_pathname),
        )
    )

    metadata["object_identifier"] = f"{identifier}:{image_filename}"
    file_set_pathname.joinpath("metadata", f"{image_filename}.mix.xml").open("w").write(
        mix_template.render(**metadata)
    )
    file = File(
        id=generate_md5(image_filename),
        use=flatten_use(UseFunctions.source, UseFormats.image),
        mdid=mdsec_items[-1].id,
        locref=f"{identifier}/data/{image_filename}",
        mimetype="image/jpeg",
        checksum=calculate_checksum(image_pathname),
    )
    file_group.files.append(file)
    source_file_identifier = file.id

    # access
    image = build_image(use=UseFunctions.service, seq=seq, version=version)
    image_filename = f"{padded_seq}.service.jpg"

    metadata["object_identifier"] = f"{identifier}:{image_filename}"
    image_pathname = file_set_pathname.joinpath("data", image_filename)
    metadata_pathname = file_set_pathname.joinpath("metadata", f"{image_filename}.mix.xml")
    image.save(image_pathname)
    metadata_pathname.open("w").write(
        mix_template.render(**metadata)
    )

    mdsec_items.append(
        Md(
            id=id_generator(),
            use=flatten_use(UseFunctions.technical),
            mdtype="NISOIMG",
            locref=f"{identifier}/metadata/{image_filename}.mix.xml",
            checksum=calculate_checksum(metadata_pathname),
        )
    )

    file = File(
        id=generate_md5(image_filename),
        group_id=source_file_identifier,
        use=flatten_use(UseFunctions.service, UseFormats.image),
        mdid=mdsec_items[-1].id,
        locref=f"{identifier}/data/{image_filename}",
        mimetype="image/jpeg",
        checksum=calculate_checksum(image_pathname)
    )
    file_group.files.append(file)

    premis_event = build_event(event_type='generate access derivative', linking_agent_type='image processing')
    mdsec_items.append(
        Md(
            id=id_generator(),
            use=flatten_use(UseFunctions.event),
            mdtype="PREMIS",
            locref=f"{identifier}/metadata/{image_filename}.premis.event.xml",
            mimetype="text/xml",
        )
    )
    file_set_pathname.joinpath("metadata", image_filename + ".premis.event.xml").open("w").write(
        premis_event_template.render(
            event=premis_event
        )
    )

    plaintext = build_plaintext(use=UseFunctions.service, seq=seq, version=version)
    text_filename = f"{padded_seq}.plaintext.txt"
    text_pathname = file_set_pathname.joinpath("data", text_filename)
    metadata_pathname = file_set_pathname.joinpath("metadata", f"{text_filename}.textmd.xml")

    text_pathname.open("w").write(plaintext)
    metadata_pathname.open("w").write(
        textmd_template.render(**metadata)
    )

    mdsec_items.append(
        Md(
            id=id_generator(),
            use=flatten_use(UseFunctions.technical),
            mdtype="TEXTMD",
            locref=f"{identifier}/metadata/{text_filename}.textmd.xml",
            checksum=calculate_checksum(metadata_pathname),
        )
    )

    file = File(
        id=generate_md5(text_filename),
        group_id=source_file_identifier,
        use=flatten_use(UseFunctions.service, UseFormats.text_plain),
        mdid=mdsec_items[-1].id,
        locref=f"{identifier}/data/{text_filename}",
        mimetype="text/plain",
        checksum=calculate_checksum(text_pathname),
    )
    file_group.files.append(file)

    premis_event = build_event(event_type='extract text', linking_agent_type='ocr processing')
    mdsec_items.append(
        Md(
            id=id_generator(),
            use=flatten_use(UseFunctions.event),
            mdtype="PREMIS",
            locref=f"{identifier}/metadata/{text_filename}.premis.event.xml",
            mimetype="text/xml",
        )
    )
    file_set_pathname.joinpath("metadata", text_filename + ".premis.event.xml").open("w").write(
        premis_event_template.render(
            event=premis_event
        )
    )

    file_set_pathname.joinpath(
        "descriptor", local_identifier + ".file_set.mets2.xml"
    ).open("w").write(
        file_set_template.render(
            object_identifier=identifier,
            alternate_identifier=f"{item_identifier.alternate_identifier}:{padded_seq}",
            file_group=file_group,
            mdsec_items=mdsec_items,
            seq=seq,
            create_date=get_datetime(),
        )
    )

    return local_identifier
