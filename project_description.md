# Project Overview
The project aims to provide a panel for design engineers and design firms to automate the process of specification projects. It allows the users to configure a project setup using different forms and selections and choose different assets to download as a package in the end.


# Tech Stack (To be completed)
- React + Vite (UI)
- Python + FastAPI + Uvicorn
- Postgres + Alembic
- Docker


# User Interface
This is the initial focus of the app for now. The goal is to have a responsive and user-friendly interface that allows users to easily configure their project setup and download the assets they need. Below is a description of pages needed.

## Landing Page
- The landing page should have a brief description of the app and its purpose. 
- It should then provide user with two choices between "Water" and "Buildings". Each choice is a square button with the an image background and the text "Water" or "Buildings" in the center. Upon clicking on either of the choices, the user should be redirected to the respective project setup page.


## Water Page
- The water page provide the user with buttons for 4 applications to choose from. These are: 
    1. Single Pump
    2. MCC Stand. Feeders
    3. Booster Set
    4. Tank level Control
- Upon clicking on any of the buttons, the user should be redirected to the respective application setup page.

## Booster Set Page
- The page should be divided into 4 sections as shown in the diagram below.
------------------------------------
|               1  header          |
------------------------------------
|config    |   single line diagram |
|          |                       |
|    2     |           3           |
|          |                       |
|          |                       |
|          -------------------------
|----------|                       |
|   4      |                       |
| assets   |                       |
------------------------------------
- Section 1, header, has the title "Motor Control Asset Library" and a brief description of the app. It also has a button "Back to Home" which redirects the user to the landing page.
- a figma prototype for this page is available [here](https://www.figma.com/make/BKivENvY8oK7KgoKNUErdY/Motor-Control-Asset-Library-Prototype?p=f)
- Section 2, Configuration, has these fields with the respective options:
    - Number of Incomers : 1, 2
    - Number of Pumps : 2, 3, 4
    - Motor Power Rate (kW) : 4, 7.5, 11, 15, 22.5, 30, 37, 45 kW
    - Type of Motor Start : DOL, Star-Delta, Soft Starter, Variable Speed Drive
    - IP Rating : IP23, IP54
    - Communication : No, ModbusTCP, ProfiNet
All fields are required, and they are all dropdowns.

- Section 3, Single Line Diagram, is a visual representation of the configuration selected in Section 2. It should be updated in real-time as the user changes the configuration in Section 2. 

- Section 4, Assets, is a checklist of all assets that the user can download. The checklist include :
    - Data Sheet
    - Single Line Diagram
    - Bill of Materials
    - Drawings
    - Specification
    - BIM Object

At the bottom of this section, there is a button "Download Package". Upon clicking this button, the user should be able to download all the assets in a zip file. The button is disabled until user completes all the fields in Section 2.

