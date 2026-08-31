#Loader file is responsible to extract the data from the datasource.The pdf which is present in lcoal
#how would i extract the data from it

from pypdf import PdfReader

def load_pdf(file_path: str) -> str :
    reader = PdfReader(file_path)
    text =" "

    for page_number.page in enumerate(reader.pages):
        extracted = page.extract_text()
        if extracted:
            text += f"\n--- Page {page_number + 1} --\n"
            text += extracted
    return text        


# Page 1
# Page 1 – Company Overview, Vision, Mission &
# Core Values
# Welcome to NextGen Tech Solutions Pvt Ltd. This Human Resources Policy document defines
# the principles, rules, and structured processes that govern employment within the organization.
# Vision:
# To become a globally respected technology company known for ethical innovation, operational
# excellence,
# and employee empowerment.
# Mission:
# To design scalable, secure, and intelligent digital solutions while fostering a high-performance
# culture
# that encourages ownership, accountability, and continuous improvement.
# Core Values:
# 1. Integrity – We act with honesty and transparency in all professional dealings.
# 2. Ownership – Employees are encouraged to take responsibility beyond assigned tasks.
# 3. Innovation – Continuous experimentation and improvement are encouraged.
# 4. Collaboration – Cross-functional teamwork drives company success.
# 5. Customer Excellence – Delivering measurable value to clients is a priority.
# Organizational Structure:
# The company operates through structured departments including Engineering, DevOps, HR, Sales,
# Marketing,
# Finance, and Operations. Each department functions under defined KPIs aligned with company
# goals.