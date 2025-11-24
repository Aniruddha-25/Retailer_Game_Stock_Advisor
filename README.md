# Retailer Game Stock Advisor

## Description



https://github.com/user-attachments/assets/1c461615-44c0-4f9a-9bcc-2758472b2246


Retailer Game Stock Advisor is a web-based machine learning application that predicts the top-selling video games for any given year. Using a Random Forest Regressor trained on 16,600+ historical game records, it helps retailers decide which games to stock by providing the top 6 recommended games along with regional sales breakdowns.

---

## Features

- On-demand model training using Random Forest Regressor (200 trees)
- Predicts top 6 best-performing games for any year (1980–2100)
- Accepts any stock quantity (1–10,000)
- Uses Platform, Genre, Publisher, and Year as model features
- Future-year forecasting with 2% annual growth
- Generates predictions for all Platform × Genre × Publisher combinations
- Game cards with rank, platform, genre, publisher & predicted sales
- Regional sales breakdown (NA, EU, JP, Other)
- Fully responsive UI for desktop, tablet, and mobile
- Fast predictions (<2 seconds)

---

## Technologies Used

- **Python**
- **Flask**
- **Pandas**
- **Scikit-Learn**
- **HTML**
- **CSS**
- **JavaScript**

- **CSV Dataset (Video Game Sales)**

---

## How to Use?

1. Clone the Repository
2. Install Required Dependencies
    ```
    pip install -r requirements.txt
    ```
3. Run the Application
    ```
    python app.py
    ```
4. Open in Browser
    ```
    http://localhost:5000
    ```
5. Workflow
6. Click 🤖 Train Model and wait for the success message
7. Enter Year and Stock Quantity
8. Click Get Recommendations
9. View the top 6 predicted games with global & regional sales

