**🤖 Try:** https://ashish-employee-leave-tracker.streamlit.app/

# 🗓️ Employee Leave Tracker

A simple, interactive web application built with Python and Streamlit for **managing and tracking employee leaves** in organizations of any size.

---

## 📖 About

**Employee Leave Tracker** is an open-source solution to streamline leave management for HR teams, managers, and employees. It provides a transparent overview of leave balances, requests, approvals, and histories—helping organizations maintain accurate records and ensuring fairness in leave allotment.

Whether you are an HR professional, team lead, or developer customizing workflows, this tool delivers:
- **Leave request workflow:** Employees can submit leave requests for review and approval.
- **Admin dashboard:** Managers/HR can view pending requests, approve/deny them, and oversee leave balances.
- **Leave history:** Track all previous leaves by employee and department.
- **Real-time leave balance calculation** for every user.
- **Raw data export options** for further analysis or reporting.

The project is ideal for small businesses, startups, or anyone needing a lightweight, customizable leave management platform.

---

## 🌟 Project Overview

**Context:**  
Organizations need an efficient way to manage and record employee leave requests, approvals, and balances. Manual tracking in spreadsheets is error-prone and lacks transparency.

**Objective:**  
Provide a free, open-source tool for employee leave management that’s easy to set up, use, and extend.

---

## ✨ Features

- **Leave Request Submission:**
  - Employees enter leave type, dates, and reason.
  - Requests are routed to managers/HR for action.

- **Approval Workflow:**
  - Admin dashboard for reviewing and managing requests.
  - Approve/deny requests, with optional comments.

- **Leave Balance Tracking:**
  - Automatic calculation of remaining leave for each employee.
  - Customizable leave categories (vacation, sick, etc.).

- **Employee Leave History:**
  - View all past leaves by user, team, or department.

- **Interactive Filtering:**
  - Filter requests/leaves by date, employee, department, status, and type.

- **Data Export:**
  - Download leave records and balances as CSV for reporting or backup.

---

## 🛠️ Technologies Used

- **Python:** Core programming language
- **Streamlit:** Interactive web dashboard
- **Pandas:** Data manipulation
- **CSV:** For data persistence (can be swapped for database integration)

---

## 🚀 Installation and Setup

To run the Leave Tracker locally:

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/ashishpant31/Employee_Leave_Tracker.git
   cd Employee_Leave_Tracker
   ```

2. **Create a Virtual Environment (Recommended):**
   ```bash
   python -m venv venv
   ```
   - **Windows:** `.\venv\Scripts\activate`
   - **macOS/Linux:** `source venv/bin/activate`

3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
   *(If requirements.txt is missing, install: streamlit, pandas, ﻿faker)*

4. **Run the Streamlit App:**
   ```bash
   streamlit run app.py
   ```
   The dashboard will open in your default web browser.

---

## 💡 Usage

- **Submit Leave Requests:** Employees fill out the leave request form.
- **Review Requests:** Admins/HR view and manage requests in the admin dashboard.
- **Track Balances:** Employees and admins can see up-to-date leave balances.
- **Export Data:** Download records for reporting or analysis.

---

## 🖼️ Dashboard Screenshots

### Leave Request Submission

<p align="center">
  <img width="1451" height="830" alt="Leave Request Submission" src="https://github.com/user-attachments/assets/f411b49d-2194-47f2-aff3-4650bdfd379f" />
</p>

### Leave Approval Dashboard

<p align="center">
  <img width="1453" height="925" alt="Leave Approval Dashboard" src="https://github.com/user-attachments/assets/bdcedceb-776c-4cad-a091-3d7cca55b2b8" />
</p>

### Employee Leave History & Balances

<p align="center">
  <img width="1451" height="930" alt="Employee Leave History" src="https://github.com/user-attachments/assets/2f9797f1-beb7-4b99-a0ce-8630cce545e6" />
</p>

### Data Export & Filtering

<p align="center">
  <img width="1435" height="808" alt="Data Export & Filtering" src="https://github.com/user-attachments/assets/74e23d9c-7eba-4cc0-9761-7dcafa602777" />
</p>

---

## 📋 Evaluation Criteria

- **Data Modeling:** Realistic, relevant datasets.
- **Analytical Thinking:** Key leave metrics and balances.
- **Product Sense:** Intuitive UX and dashboard layout.
- **Code Quality:** Clean, well-commented Python code.
- **Insights:** Dashboard delivers meaningful leave management data.
- **Documentation:** Clear setup and usage instructions.

---

## 🤝 Contributing

Contributions are welcome!
- Fork the repo, create a branch, commit your changes, push, and open a pull request.

---

## 📄 License

This project is licensed under the MIT License. See the `LICENSE` file.

---

## 📧 Contact

For questions or feedback, please reach out via [GitHub Issues](https://github.com/ashishpant31/Employee_Leave_Tracker/issues).

---

## ⚠️ Important: Using `.gitignore` to Exclude Virtual Environments

Always use a `.gitignore` file to prevent committing your local Python environment and system files:

```
venv/
*.pyc
__pycache__/
.env
.DS_Store
```

This keeps your repository clean and focused on code.

---

For more information, check out [Streamlit Documentation](https://docs.streamlit.io/) and [GitHub .gitignore best practices](https://github.com/github/gitignore).
