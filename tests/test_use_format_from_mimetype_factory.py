import pytest
from dor.builders.parts import UseFormat


def test_from_mimetype_application():
    # Test application MIME types
    assert UseFormat.from_mimetype("application/annotation+json") == UseFormat.text_annotations

    with pytest.raises(ValueError):
        UseFormat.from_mimetype("application/json")

    with pytest.raises(ValueError):
        UseFormat.from_mimetype("application/xml")


def test_from_mimetype_audio():
    # Test audio MIME types
    assert UseFormat.from_mimetype("audio/mp3") == UseFormat.audio
    assert UseFormat.from_mimetype("audio/wav") == UseFormat.audio
    assert UseFormat.from_mimetype("audio/ogg") == UseFormat.audio


def test_from_mimetype_image():
    # Test image MIME types
    assert UseFormat.from_mimetype("image/jpeg") == UseFormat.image
    assert UseFormat.from_mimetype("image/png") == UseFormat.image
    assert UseFormat.from_mimetype("image/tiff") == UseFormat.image
    assert UseFormat.from_mimetype("image/gif") == UseFormat.image


def test_from_mimetype_text():
    # Test text MIME types
    assert UseFormat.from_mimetype("text/plain") == UseFormat.text_plain
    assert UseFormat.from_mimetype("text/plain; charset=UTF-8") == UseFormat.text_plain
    assert UseFormat.from_mimetype("text/annotation+xml") == UseFormat.text_annotations
    assert UseFormat.from_mimetype("text/coordinate") == UseFormat.text_coordinates
    assert UseFormat.from_mimetype("text/html") == UseFormat.text_encoded
    assert UseFormat.from_mimetype("text/xml") == UseFormat.text_encoded


def test_from_mimetype_video():
    # Test video MIME types (should return audiovisual)
    assert UseFormat.from_mimetype("video/mp4") == UseFormat.audiovisual
    assert UseFormat.from_mimetype("video/mpeg") == UseFormat.audiovisual
    assert UseFormat.from_mimetype("video/quicktime") == UseFormat.audiovisual


def test_from_mimetype_with_parameters():
    # Test MIME types with parameters
    assert UseFormat.from_mimetype("text/plain; charset=UTF-8") == UseFormat.text_plain
    assert UseFormat.from_mimetype("text/plain; charset=US-ASCII") == UseFormat.text_plain


def test_from_mimetype_invalid():
    # Test invalid MIME types
    with pytest.raises(ValueError):
        UseFormat.from_mimetype("invalid/type")

    with pytest.raises(ValueError):
        UseFormat.from_mimetype("application/json")

    with pytest.raises(ValueError):
        UseFormat.from_mimetype("")


def test_from_mimetype_malformed():
    # Test malformed MIME types
    with pytest.raises(ValueError):
        UseFormat.from_mimetype("image")

    with pytest.raises(ValueError):
        UseFormat.from_mimetype("/jpeg")

    with pytest.raises(ValueError):
        UseFormat.from_mimetype("image/")
