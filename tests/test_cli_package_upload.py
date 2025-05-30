from typer.testing import CliRunner

from dor.cli.main import app as cli_app


runner = CliRunner()


def test_package_upload_fails_with_fake_path():
    result = runner.invoke(
        cli_app,
        [
            "package",
            "upload",
            "some/fake/path"
        ],
    )
    assert result.exit_code == 1
