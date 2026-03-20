import pytest

from pipeline.cli import build_parser


def test_parser_run_subcommand_with_source():
    args = build_parser().parse_args(["run", "--source", "newhospitals"])
    assert args.cmd == "run"
    assert args.source == "newhospitals"
    assert args.all is False


def test_parser_run_subcommand_with_all():
    args = build_parser().parse_args(["run", "--all"])
    assert args.cmd == "run"
    assert args.all is True
    assert args.source is None


def test_parser_run_subcommand_requires_one_of_source_or_all():
    parser = build_parser()
    with pytest.raises(SystemExit):
        parser.parse_args(["run"])


def test_parser_scheduler_subcommand():
    args = build_parser().parse_args(["scheduler"])
    assert args.cmd == "scheduler"
