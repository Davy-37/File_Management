from pathlib import Path

import pytest

from File_Management.search.search_by_word import (
	contains_word,
	count_occurrences,
	find_lines,
	get_context,
	search_by_extension,
	search_in_folder,
)


def test_search_by_extension_accepts_string_or_list_and_normalizes_dot(tmp_path):
	text_file = tmp_path / "notes.txt"
	csv_file = tmp_path / "data.csv"
	(tmp_path / "image.png").touch()
	text_file.touch()
	csv_file.touch()

	assert set(search_by_extension(tmp_path, "txt")) == {text_file}
	assert set(search_by_extension(tmp_path, [".txt", "csv"])) == {
		text_file,
		csv_file,
	}


def test_search_by_extension_respects_recursive_option(tmp_path):
	direct_file = tmp_path / "direct.txt"
	nested_dir = tmp_path / "nested"
	nested_dir.mkdir()
	nested_file = nested_dir / "nested.txt"
	direct_file.touch()
	nested_file.touch()

	assert set(search_by_extension(tmp_path, ".txt", recursive=False)) == {direct_file}
	assert set(search_by_extension(tmp_path, ".txt")) == {direct_file, nested_file}


def test_search_by_extension_returns_empty_for_missing_directory(tmp_path):
	assert search_by_extension(tmp_path / "missing", ".txt") == []


@pytest.mark.parametrize(
	("content", "keyword", "options", "expected"),
	[
		("A quick FOX", "fox", {}, True),
		("A quick FOX", "fox", {"ignore_case": False}, False),
		("the foxes", "fox", {"whole_word": True}, False),
		("the fox!", "fox", {"whole_word": True}, True),
	],
)
def test_contains_word_options(tmp_path, content, keyword, options, expected):
	file_path = tmp_path / "sample.txt"
	file_path.write_text(content, encoding="utf-8")

	assert contains_word(file_path, keyword, **options) is expected


def test_find_lines_returns_matching_line_numbers_and_contents(tmp_path):
	file_path = tmp_path / "sample.txt"
	file_path.write_text("First fox\nno match\nFOX again\n", encoding="utf-8")

	assert find_lines(file_path, "fox") == [(1, "First fox"), (3, "FOX again")]


def test_count_occurrences_counts_repeated_matches(tmp_path):
	file_path = tmp_path / "sample.txt"
	file_path.write_text("cat CAT caterpillar\n", encoding="utf-8")

	assert count_occurrences(file_path, "cat") == 3
	assert count_occurrences(file_path, "cat", whole_word=True) == 2


def test_get_context_returns_lines_before_and_after_match(tmp_path):
	file_path = tmp_path / "sample.txt"
	file_path.write_text("one\ntwo\nneedle\nfour\nfive\n", encoding="utf-8")

	assert get_context(file_path, "needle", lines_around=1) == [
		{"line_num": 3, "context": ["two", "needle", "four"]}
	]


def test_get_context_returns_partial_context_at_end_of_file(tmp_path):
	file_path = tmp_path / "sample.txt"
	file_path.write_text("one\nneedle\nthree\n", encoding="utf-8")

	assert get_context(file_path, "needle", lines_around=2) == [
		{"line_num": 2, "context": ["one", "needle", "three"]}
	]


def test_search_in_folder_filters_extensions_and_searches_recursively(tmp_path):
	nested_dir = tmp_path / "nested"
	nested_dir.mkdir()
	matching_file = nested_dir / "match.txt"
	wrong_extension = tmp_path / "other.csv"
	matching_file.write_text("find this needle", encoding="utf-8")
	wrong_extension.write_text("find this needle", encoding="utf-8")

	assert search_in_folder(tmp_path, "needle", extensions="txt") == [matching_file]
	assert search_in_folder(tmp_path, "needle", recursive=False) == [wrong_extension]
