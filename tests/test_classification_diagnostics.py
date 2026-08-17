from rekordbox_library_intelligence.classification import (
    ClassificationSuggestion,
)
from rekordbox_library_intelligence.classification_benchmark import (
    GroundTruth,
)
from rekordbox_library_intelligence.classification_diagnostics import (
    build_classification_diagnostics,
    format_classification_diagnostics,
)


def suggestion(
    track_id: int,
    energy: str | None,
    function: str | None,
) -> ClassificationSuggestion:
    return ClassificationSuggestion(
        track_id=track_id,
        artist="Example Artist",
        title=f"Track {track_id}",
        style=None,
        elements=(),
        energy=energy,
        function=function,
        confidence="LOW",
        reasons=(),
    )


def truth(
    track_id: int,
    energy: str | None,
    function: str | None,
) -> GroundTruth:
    return GroundTruth(
        track_id=track_id,
        style=None,
        elements=(),
        energy=energy,
        function=function,
    )


def test_energy_diagnostics():
    suggestions = [
        suggestion(
            1,
            "Strong",
            None,
        ),
        suggestion(
            2,
            "Peak",
            None,
        ),
        suggestion(
            3,
            None,
            None,
        ),
    ]

    ground_truth = {
        1: truth(
            1,
            "Strong",
            None,
        ),
        2: truth(
            2,
            "Strong",
            None,
        ),
        3: truth(
            3,
            "Lift",
            None,
        ),
    }

    diagnostics = (
        build_classification_diagnostics(
            suggestions,
            ground_truth,
        )
    )

    energy = diagnostics.energy

    assert energy.evaluated == 3

    assert (
        energy.predictions_present
        == 2
    )

    assert (
        energy.missing_predictions
        == 1
    )

    assert energy.correct == 1

    assert (
        energy.mismatch_pairs[
            ("Strong", "Peak")
        ]
        == 1
    )

    assert (
        energy.mismatch_pairs[
            ("Lift", "-")
        ]
        == 1
    )


def test_function_diagnostics():
    suggestions = [
        suggestion(
            1,
            "Peak",
            None,
        ),
        suggestion(
            2,
            "Warm",
            "Opener",
        ),
    ]

    ground_truth = {
        1: truth(
            1,
            "Peak",
            "Weapon",
        ),
        2: truth(
            2,
            "Warm",
            "Opener",
        ),
    }

    diagnostics = (
        build_classification_diagnostics(
            suggestions,
            ground_truth,
        )
    )

    function = diagnostics.function

    assert function.evaluated == 2

    assert (
        function.predictions_present
        == 1
    )

    assert (
        function.missing_predictions
        == 1
    )

    assert function.correct == 1

    assert (
        function.mismatch_pairs[
            ("Weapon", "-")
        ]
        == 1
    )


def test_format_diagnostics():
    suggestions = [
        suggestion(
            1,
            "Peak",
            None,
        )
    ]

    ground_truth = {
        1: truth(
            1,
            "Strong",
            "Weapon",
        )
    }

    diagnostics = (
        build_classification_diagnostics(
            suggestions,
            ground_truth,
        )
    )

    output = (
        format_classification_diagnostics(
            diagnostics
        )
    )

    assert (
        "Classification Diagnostics"
        in output
    )

    assert "ENERGY" in output
    assert "FUNCTION" in output

    assert (
        "Strong -> Peak"
        in output
    )

    assert (
        "Weapon -> -"
        in output
    )

    assert "Coverage:" in output
    assert "Accuracy:" in output