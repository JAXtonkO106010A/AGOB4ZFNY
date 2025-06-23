# 📅 Week 2: AWS Cloud Services Basics – EC2, S3 & CloudWatch

## ✅ Objective
This week's tasks focused on deploying basic AWS infrastructure and understanding core services like EC2, S3, and CloudWatch. It included launching an EC2 instance, configuring billing alerts, uploading to S3 via PowerShell, and identifying IAM/connection issues.

---

## 🛠️ Services Used
- **Amazon EC2:** Instance creation & access
- **Amazon S3:** Bucket creation & file upload (via PowerShell)
- **Amazon CloudWatch:** Billing alerts
- **IAM Roles & Permissions**
- **Remote Desktop & PowerShell**

---
![image1](https://github.com/user-attachments/assets/efe27225-701f-49ca-a478-986b88a2c2dc)
![image2](https://github.com/user-attachments/assets/d7368b41-4ae4-4023-91a7-f8b2121c752f)
![image3](https://github.com/user-attachments/assets/b09e4742-b870-4545-8bcc-11b31cbc9ba7)
![image4](https://github.com/user-attachments/assets/54c0bb64-8468-4ea6-86b6-4e22cef7441d)
![image5](https://github.com/user-attachments/assets/92b4ff22-32d2-40a1-8cd9-45bdfb052f6f)
![image6](https://github.com/user-attachments/assets/3b4b2cd2-9234-4e0a-9cfa-fe4f2506eb97)
![image7](https://github.com/user-attachments/assets/445c33e9-919f-4d39-95b3-0dc6d2acb20a)
![image8](https://github.com/user-attachments/assets/18113c87-a6a3-4ec5-9e84-83d7761e23b8)
![image9](https://github.com/user-attachments/assets/02680cd4-97b9-4dde-b203-0e25657c3ce1)

## 🔍 Activities Performed

### 1. ✅ Created a Billing Alarm in CloudWatch  
Alarm was set to trigger if estimated charges exceed $10.

---

### 2. ✅ Created S3 Bucket `academics-raw-lok`  
Region: US East (N. Virginia)

---

### 3. ✅ Created folders inside the S3 Bucket  
Folders: `faculty-performance/`, `panel-members/`, `preliminary-feedback/`

---

### 4. ✅ Launched EC2 Windows Instance (t3.micro)  
Instance ID: i-0e95d50239efafa0d

---

### 5. ✅ Logged into EC2 via RDP  
EC2 instance desktop accessed using Remote Desktop.

---

### 6. ✅ Uploaded File from EC2 using PowerShell  
```powershell
write-s3object -bucket academics-raw-lok -file "C:\Users\Administrator\Documents\Panel-members.csv" `
-key "academics/panel-members/year-2025/quarter-1/server-AGVS-LOK/Panel-members.csv"

----

