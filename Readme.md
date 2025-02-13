# Zero-Dose Project: Identifying Unvaccinated Children 

## Overview
This repository hosts a disease modeling framework focused on **identifying zero-dose children**—those who have never received any routine vaccinations. The model leverages **tetanus vaccination data** as a **pivot** to infer gaps in immunization and guide interventions. The primary intervention under consideration is the **Pentacel vaccine**, which protects against:

- **Diphtheria**
- **Tetanus**
- **Pertussis**
- **Polio**
- **Haemophilus influenzae type b (Hib)**

Currently, only tetanus data is available, making it the key indicator for assessing immunization gaps.

## Goals
- Develop a **disease model** to simulate **tetanus transmission and immunity**.
- Implement **Pentacel vaccination interventions**, using tetanus as a proxy.
- Expand the model to include the remaining diseases targeted by Pentacel in future iterations.

## Features (Planned)
- **Agent-based modeling framework** (built using [Starsim](https://github.com/InstituteforDiseaseModeling/starsim))
- **Tetanus immunization data analysis** to infer zero-dose status
- **Vaccination coverage estimation** using tetanus as a reference
- **Intervention strategies** to improve routine immunization uptake
- **Scalability** to incorporate diphtheria, pertussis, polio, and Hib in later versions

## Installation
To set up the environment, clone this repository and install the required dependencies:

```bash
# Clone the repository
git clone https://github.com/starsimhub/zdsim.git
cd zdsim

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Usage
A basic simulation run can be executed using:

```bash
python run_simulation.py
```

The model outputs will provide insights into **zero-dose children and vaccination gaps**, guiding **Pentacel vaccine interventions**.

## Contributing
Contributions are welcome! If you would like to contribute, please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature-name`)
3. Commit your changes (`git commit -m "Description of changes"`)
4. Push to the branch (`git push origin feature-name`)
5. Open a Pull Request

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contact
For questions or collaborations, feel free to open an issue or reach out to the repository maintainers.

