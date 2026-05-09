#!/usr/bin/env python3
"""Utilities for transcription evaluation metrics."""

from __future__ import annotations

import re
import unicodedata


PUNCTUATION_PATTERN = re.compile(r"[、。.,!?！？:：;；「」『』（）()\[\]{}〈〉《》【】…\-ー〜～]")
WHITESPACE_PATTERN = re.compile(r"\s+")
LATIN_TOKEN_PATTERN = re.compile(r"[A-Za-z0-9]+(?:[._:/-][A-Za-z0-9]+)*")


def normalize_text(text: str) -> str:
    text = unicodedata.normalize("NFKC", text)
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = WHITESPACE_PATTERN.sub(" ", text).strip()
    return text


def remove_punctuation(text: str) -> str:
    return PUNCTUATION_PATTERN.sub("", text)


def tokenize_for_wer(text: str) -> list[str]:
    text = normalize_text(text)
    tokens: list[str] = []
    index = 0
    while index < len(text):
        match = LATIN_TOKEN_PATTERN.match(text, index)
        if match:
            tokens.append(match.group(0).lower())
            index = match.end()
            continue
        char = text[index]
        if char.isspace():
            index += 1
            continue
        if PUNCTUATION_PATTERN.fullmatch(char):
            tokens.append(char)
        else:
            tokens.append(char)
        index += 1
    return tokens


def levenshtein_distance(reference: list[str], hypothesis: list[str]) -> int:
    if not reference:
        return len(hypothesis)
    if not hypothesis:
        return len(reference)

    previous = list(range(len(hypothesis) + 1))
    for i, ref_item in enumerate(reference, start=1):
        current = [i]
        for j, hyp_item in enumerate(hypothesis, start=1):
            substitution_cost = 0 if ref_item == hyp_item else 1
            current.append(
                min(
                    previous[j] + 1,
                    current[j - 1] + 1,
                    previous[j - 1] + substitution_cost,
                )
            )
        previous = current
    return previous[-1]


def cer(reference: str, hypothesis: str) -> float:
    ref = list(normalize_text(reference))
    hyp = list(normalize_text(hypothesis))
    if not ref:
        return 0.0 if not hyp else 1.0
    return levenshtein_distance(ref, hyp) / len(ref)


def cer_without_punctuation(reference: str, hypothesis: str) -> float:
    ref = remove_punctuation(normalize_text(reference))
    hyp = remove_punctuation(normalize_text(hypothesis))
    if not ref:
        return 0.0 if not hyp else 1.0
    return levenshtein_distance(list(ref), list(hyp)) / len(ref)


def wer(reference: str, hypothesis: str) -> float:
    ref = tokenize_for_wer(reference)
    hyp = tokenize_for_wer(hypothesis)
    if not ref:
        return 0.0 if not hyp else 1.0
    return levenshtein_distance(ref, hyp) / len(ref)


def proper_noun_misses(reference: str, hypothesis: str, proper_nouns: list[str]) -> tuple[int, int]:
    normalized_ref = normalize_text(reference)
    normalized_hyp = normalize_text(hypothesis)
    total = 0
    misses = 0
    for noun in proper_nouns:
        term = normalize_text(noun)
        if not term or term not in normalized_ref:
            continue
        total += 1
        if term not in normalized_hyp:
            misses += 1
    return misses, total
