# Submission fields

Title: Misleading Identifiers Change What Code Traces Write

Type: Short paper

Suggested area: NLP and Code Models

TL;DR: Models can write values suggested by misleading identifiers while correct digits remain decodable; source-expression examples reduce those errors.

Abstract:

Misleading variable names can change the values a language model reports even when the correct values remain readable in its internal activity. We extend Kudo et al.'s arithmetic study to Python programs, asking seven models to report each assigned value. Renaming a variable holding a list's length to suggest a sum makes three models more often write the sum. Yet predictors trained on other programs recover the correct value with 95.5–99.7% accuracy immediately before these wrong writes. Worked examples that include the code expression beside each value sharply reduce the errors; descriptive text of the same length leaves many of them. A correct internal readout therefore cannot certify a written trace. The model can still report the name-suggested value. Including source expressions in worked examples offers a practical way to improve trace reliability.

Authors, submission history, preferred venue, preprint declaration and service contributor require author completion in OpenReview.
