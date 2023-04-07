def get_linkedin_profile() -> dict:
    return {
        "id": "123456789",
        "firstName": "Jane",
        "lastName": "Doe",
        "headline": "Senior Software Engineer at TechCorp Inc.",
        "summary": "An experienced software engineer with a strong background in developing high-quality applications. Passionate about technology and always seeking to learn and improve.",
        "positions": {
            "_total": 3,
            "values": [
                {
                    "id": 987654321,
                    "title": "Senior Software Engineer",
                    "company": {
                        "id": 12345,
                        "name": "TechCorp Inc.",
                        "type": "Privately Held",
                        "industry": "Information Technology and Services"
                    },
                    "startDate": {
                        "month": 3,
                        "year": 2021
                    },
                    "duration": "10 months",
                    "description": """- Developing and maintaining the company's flagship application
- Implementing new features and ensuring high code quality
- Collaborating with cross-functional teams to enhance the product""",
                    "isCurrent": True
                },
                {
                    "id": 123456789,
                    "title": "Software Engineer",
                    "company": {
                        "id": 23456,
                        "name": "Innovative Solutions Ltd.",
                        "type": "Privately Held",
                        "industry": "Information Technology and Services"
                    },
                    "startDate": {
                        "month": 8,
                        "year": 2019
                    },
                    "endDate": {
                        "month": 2,
                        "year": 2021
                    },
                    "duration": "1 year, 7 months",
                    "description": """- Developed, tested, and deployed various software applications
- Contributed to several successful projects with an emphasis on quality and timeliness
- Participated in code reviews and shared best practices""",
                    "isCurrent": False
                },
                {
                    "id": 567891234,
                    "title": "Junior Developer",
                    "company": {
                        "id": 34567,
                        "name": "StartupXYZ",
                        "type": "Privately Held",
                        "industry": "Computer Software"
                    },
                    "startDate": {
                        "month": 6,
                        "year": 2018
                    },
                    "endDate": {
                        "month": 7,
                        "year": 2019
                    },
                    "duration": "1 year, 1 month",
                    "description": """- Assisted the development team in creating, debugging, and testing web applications
- Learned the industry's best practices
- Gained hands-on experience with web development technologies""",
                    "isCurrent": False
                }
            ]
        }
    }