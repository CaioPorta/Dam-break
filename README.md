# Dam Break Project

Project developed for UNESP-FES. It is about the study of non-Newtonian liquids through a dam break.
The system is controlled by a gate and an inclined channel.
The HMI has been made using Python (PyQt5).
The control itself has been made using Arduino UNO and some peripherals such as step motors, pneumatic system, and end-switches.

---

## Introduction to Dam Break Study

Dam break refers to the collapse of an infinite or finite volume of fluid, particles, or their mixture onto a horizontal or inclined channel.
It represents a wide range of practical problems that are of great engineering importance. The collapse of water-reserving dams or earth-filling
tailings dams are among the most widely known examples. The failure of these dams may cause catastrophic damages to both human life and properties. For
example, the overflow of reservoir water of Vajont dam in Italy caused by a landslide in 1963 killed 1910 people. More recently, the collapse of Situ
Gintung water dam in Tangerang of Indonesia in 2009 claimed nearly 100 lives. Several recent devastating failures of mine/waste tailings dams have drawn
global attentions on their threat to the environment and human life. One example is the collapse of Bento Rodrigues tailings dam occurring in Mariana,
Brazil, on Nov. 5, 2015. The collapsed slurry wave flooded the town of Bento Rodrigues, killed at least 17 people and polluted several nearby rivers and
over 15 km2 of land. A tailings dam of jade mine collapsed in northern Myanmar on Nov. 21, 2015 killed at least 113 people. Indeed, there have been over
40 similar major failures of tailings dams reported around the world since 2000.

The scientific value of dam break has long been recognized, as an idealized problem for benchmark and verification for a range of theories and approaches
in both mathematics and physics. In as early as 1892, Ritter has derived a theoretical solution for the flow front of water based on a simple dam break
model. Late analytical studies have examined various aspects of dam break, including the effect of flow resistance. The majority of past studies on dam
break considered the collapse of either pure fluids or dry particles, with only quite a few on particle-water mixtures. The focus of the present study is
placed on the collapsing of a mixture composed by granular particles and non-Newtonian fluids, in reference to engineering problems relevant to tailings
dams or environmental flows such as volcanic lava, slurry and mud flows wherein the fluid involved is typically non-Newtonian [21]. Dam break of pure
non-Newtonian fluids such as slurry and gel has been studied in [13, 14]. Other examples involving non-Newtonian fluids include the slump tests on fresh
concrete in civil engineering and Bostwick tests for salad dressings in food industry. Consideration of non-Newtonian fluids indeed enables better
explorations of more complex natural flows such as slurry than considering Newtonian fluids like water only. Conventional continuum-based studies on dam
break have commonly considered a particle-fluid mixture as an equivalent fluid or two fluids. They have largely neglected the intricate interactions
between the fluid and the particle phases which could affect significantly the collapse behavior of the mixture. In this study, a coupled CFD-DEM approach
is employed to investigate the collapse of a mixture consisting of fluid and particles, where we will demonstrate that fluid-particle interactions within
the mixture can be well captured. The CFD and DEM are used to model the fluid and particle phases in the mixture, respectively. The interactions between
the fluid and particles are considered by exchanging fluid-particle interaction forces between the CFD and DEM computations. The coupled CFD-DEM simulations
can capture both micro and macro flow characteristics during dam break, which could offer new insights into the microstructural origins underpinning
macroscopic collapse and flow of a mixture.

[Reference](https://jzhao.people.ust.hk/home/PDFs/Dambreak-PT2018.pdf)

---

## Project Overview

This project is a **hardware-in-the-loop control system** for studying dam break phenomena, specifically the behavior of non-Newtonian fluids flowing
down an inclined channel. It bridges computational fluid dynamics experiments with real-time physical control.

### What It Does

The application provides a graphical interface (HMI) that controls a physical experimental setup consisting of:

- **A gate mechanism** - controls the release of fluid material
- **An inclined channel** - where the dam break flow occurs
- **Step motors** - for precise positioning and angle adjustment
- **A pneumatic system** - for gate actuation
- **End-switches** - for safety limits

### Architecture

```
Dam-break/
├── src/                          # Python source code
│   ├── Dambreak.py              # Main PyQt5 HMI application
│   ├── config.py                # Configuration & constants
│   ├── ArduinoComm.py           # Serial communication layer
│   ├── DBManager.py             # SQLite database management
│   ├── WorkerThread.py          # Background threading
│   ├── ui_components.py         # UI component helpers
│   ├── macro_manager.py         # Macro execution logic
│   └── Dambreak.spec            # PyInstaller spec file
├── images/                       # UI assets & icons
├── arduino/                      # Arduino sketches
│   └── TESTE_ARDUINO/
├── data/                         # Database
│   └── Database_Dambreak.db
├── docs/                         # Documentation
│   └── Guia de desenvolvimento/
├── Dambreak_IHM_icon.ico         # Application icon
├── Gerador de Executavel.txt     # Build instructions
└── README.md
```

### Key Modules

| Module | Purpose |
|--------|---------|
| `Dambreak.py` | Main PyQt5 HMI application - the user interface with macro management, manual control, and status monitoring |
| `ArduinoComm.py` | Serial communication layer - sends control commands (position, velocity, acceleration, inclination) to the Arduino UNO via USB |
| `DBManager.py` | Data persistence layer - manages an SQLite database (`data/Database_Dambreak.db`) for storing macros, command history, and application cache |
| `WorkerThread.py` | Background threading - handles continuous value adjustments (increment/decrement) for acceleration, velocity, position, and inclination without blocking the UI |
| `config.py` | Centralized configuration - parameter limits, screen ratios, themes, fonts, paths, and constants |
| `ui_components.py` | UI helper functions - creates styled buttons, labels, textboxes, and layout components |
| `macro_manager.py` | Macro execution engine - handles recording, saving, and playback of macro sequences |

### Key Features

- **Macro system** - Record, save, edit, and playback sequences of up to 8 macros with configurable parameters (position `h`, velocity `v`, acceleration `a`, inclination `α`, delay, and cycle count)
- **Manual control** - Real-time adjustment of motion parameters with 6 precision levels (1, 1/2, 1/4, 1/8, 1/16, 1/32)
- **Command history** - Logs all executed commands to SQLite for post-experiment analysis
- **Theme support** - Light/dark background toggle
- **Executable build** - Can be packaged as a standalone Windows `.exe` using PyInstaller

### Communication Protocol

Commands are sent to the Arduino as binary strings encoded in UTF-8. Each parameter (position, velocity, acceleration, inclination) is converted to a 17-bit binary representation and concatenated into a single message. The Arduino interprets these values to drive the step motors and control the pneumatic system.

### Dependencies

- Python 3.9
- PyQt5
- pyserial
- SQLite3 (built-in)

### Running the Application

```bash
cd src
python Dambreak.py
```

### Building the Executable

```bash
# From project root
pyinstaller --onefile --noconsole -i Dambreak_IHM_icon.ico src\Dambreak.py
```

The compiled executable is located at `dist/Dambreak.exe`.

> **Note:** See `Gerador de Executavel.txt` for detailed build instructions.

### Project Structure

| Directory/File | Description |
|----------------|-------------|
| `src/` | All Python source code |
| `images/` | UI assets (icons, logos, theme images) |
| `arduino/` | Arduino test sketches |
| `data/` | SQLite database file |
| `docs/` | Development documentation and guides |
| `build/` | PyInstaller build artifacts (generated) |
| `dist/` | Distribution output including executable (generated) |
| `__pycache__/` | Python bytecode cache (generated) |

---

## Development Notes

- **Author:** Caio Moreira Porta (CaioPorta)
- **Created:** November 2021
- **For:** Professor Geraldo de Freitas Maciel - UNESP/FEIS
- **Version:** Alpha 0.0.1
- **Last modified:** December 3, 2021
