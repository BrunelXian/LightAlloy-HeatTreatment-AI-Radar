# DSC curve fingerprints directly encode mechanical properties of aluminum alloys

## Metadata
- Paper ID: `43b5af7e4af9efab`
- Title: DSC curve fingerprints directly encode mechanical properties of aluminum alloys
- Authors: Lukas Pichlmann, Samuel Studer, Aurel R. Arnoldt, Paul Oberhauser, Johannes A. Österreicher
- Year: 2026
- Venue: arXiv
- DOI: 
- URL: http://arxiv.org/abs/2603.19905v1
- Source: arXiv
- Manual status: core
- Manual notes: Must-read paper for heat-treatment ML review.
- Machine screening decision: CORE
- Relevance score: 18
- Screening reason: positive: aluminum, alloy, aging, precipitation, machine learning, optimization

## Tags
- alloy_system: Aluminium alloy, Al-Mg-Si
- heat_treatment_process: Artificial ageing
- property_target: Tensile strength, Yield strength, Ductility
- ml_method: 
- research_position: Process optimisation

## Abstract

Differential scanning calorimetry (DSC) is a standard tool for studying precipitation and phase transformations in aluminum alloys, yet its relation to mechanical performance has so far remained mostly indirect. Here, we demonstrate that DSC curves themselves act as fingerprints that directly encode mechanical properties. Four representative 6xxx series alloys (Al-Mg-Si) were subjected to different natural and artificial aging regimens, followed by DSC heat-flow measurements and tensile testing. Machine learning models trained on the thermograms predicted yield strength, ultimate tensile strength, and uniform elongation in five-fold grouped cross-validation, with the best model (Lasso) achieving R^2 values of 0.93, 0.86, and 0.87 and mean absolute errors of 14.3 MPa, 11.1 MPa, and 1.5 percent, respectively. Leave-one-alloy-out evaluation with sparse calibration using anchor samples further demonstrated generalization across alloy chemistries. While direct prediction on unseen alloy data degraded performance substantially, inclusion of as few as one to two anchor conditions from the target alloy recovered predictive accuracy, approaching that of the standard cross-validation. Feature importance analysis revealed that the 230 to 270 C region, associated with precipitation of the primary hardening phase beta'', contributed most strongly to predictive accuracy, providing direct mechanistic validation of the model. These findings establish DSC as a diagnostic tool that can serve as a rapid proxy for mechanical property evaluation, enabling accelerated alloy screening, process optimization, and integration of thermal analysis into data-driven manufacturing.

## Review Notes
- Why it matters: Connects heat-treatment knowledge to process optimisation and decision support.
- Potential review section: Process optimisation and decision support
- Reading priority: High
