const courses = [
  {
    "course_code": "CSE 121",
    "course_title": "Introduction to Computer Programming ICourse"
  },
  {
    "course_code": "CSE 122",
    "course_title": "Introduction to Computer Programming IICourse"
  },
  {
    "course_code": "CSE 123",
    "course_title": "Introduction to Computer Programming IIICourse"
  },
  {
    "course_code": "CSE 143",
    "course_title": "Computer Programming IICoursePrerequisite:\u00c2\u00a0CSE 142."
  },
  {
    "course_code": "CSE 160",
    "course_title": "Data ProgrammingCourse"
  },
  {
    "course_code": "CSE 163",
    "course_title": "Intermediate Data ProgrammingCoursePrerequisite:\u00c2\u00a0Either CSE 122, CSE 123, CSE 142, CSE 143, or CSE 160."
  },
  {
    "course_code": "CSE 190",
    "course_title": "Current Topics in Computer Science and EngineeringCourse"
  },
  {
    "course_code": "CSE 311",
    "course_title": "Foundations of Computing ICoursePrerequisite:\u00c2\u00a0A minimum grade of 2.0 in either CSE 123 or CSE 143; and MATH 126 or MATH 136."
  },
  {
    "course_code": "CSE 312",
    "course_title": "Foundations of Computing IICoursePrerequisite:\u00c2\u00a0CSE 311."
  },
  {
    "course_code": "CSE 331",
    "course_title": "Software Design and ImplementationCoursePrerequisite:\u00c2\u00a0A minimum grade of 2.0 in either CSE 123 or CSE 143."
  },
  {
    "course_code": "CSE 332",
    "course_title": "Data Structures and ParallelismCoursePrerequisite:\u00c2\u00a0CSE 311."
  },
  {
    "course_code": "CSE 333",
    "course_title": "Systems ProgrammingCoursePrerequisite:\u00c2\u00a0CSE 351."
  },
  {
    "course_code": "CSE 341",
    "course_title": "Programming LanguagesCoursePrerequisite:\u00c2\u00a0CSE 123 or CSE 143."
  },
  {
    "course_code": "CSE 344",
    "course_title": "Introduction to Data ManagementCoursePrerequisite:\u00c2\u00a0CSE 311."
  },
  {
    "course_code": "CSE 351",
    "course_title": "The Hardware/Software InterfaceCoursePrerequisite:\u00c2\u00a0CSE 123 or CSE 143."
  },
  {
    "course_code": "CSE 369",
    "course_title": "Introduction to Digital DesignCoursePrerequisite:\u00c2\u00a0CSE 311."
  },
  {
    "course_code": "CSE 371",
    "course_title": "Design of Digital Circuits and SystemsCoursePrerequisite:\u00c2\u00a0Either E E 205 or E E 215; either E E 271 or CSE 369."
  },
  {
    "course_code": "CSE 373",
    "course_title": "Data Structures and AlgorithmsCoursePrerequisite:\u00c2\u00a0CSE 123 or CSE 143."
  },
  {
    "course_code": "CSE 390",
    "course_title": "Special Topics in Computer Science and EngineeringCourse"
  },
  {
    "course_code": "CSE 391",
    "course_title": "System and Software ToolsCoursePrerequisite:\u00c2\u00a0Either CSE 122, CSE 123, or CSE 143."
  },
  {
    "course_code": "CSE 403",
    "course_title": "Software EngineeringCoursePrerequisite:\u00c2\u00a0CSE 331; CSE 332."
  },
  {
    "course_code": "CSE 412",
    "course_title": "Introduction to Data VisualizationCoursePrerequisite:\u00c2\u00a0Either CSE 123, CSE 143, or CSE 163."
  },
  {
    "course_code": "CSE 414",
    "course_title": "Introduction to Database SystemsCoursePrerequisite:\u00c2\u00a0A minimum grade of 2.5 in either CSE 123, CSE 143, or CSE 163."
  },
  {
    "course_code": "CSE 415",
    "course_title": "Introduction to Artificial IntelligenceCoursePrerequisite:\u00c2\u00a0CSE 373."
  },
  {
    "course_code": "CSE 416",
    "course_title": "Introduction to Machine LearningCoursePrerequisite:\u00c2\u00a0Either CSE 123, CSE 143, CSE 160, or CSE 163; and either STAT 311, STAT 390, STAT 391, IND E 315, MATH 394/STAT 394, STAT 395/MATH 395, or Q SCI 381."
  },
  {
    "course_code": "CSE 421",
    "course_title": "Introduction to AlgorithmsCoursePrerequisite:\u00c2\u00a0CSE 312; CSE 332."
  },
  {
    "course_code": "CSE 422",
    "course_title": "Toolkit for Modern AlgorithmsCoursePrerequisite:\u00c2\u00a0CSE 312; CSE 332; and MATH 208."
  },
  {
    "course_code": "CSE 426",
    "course_title": "CryptographyCoursePrerequisite:\u00c2\u00a0CSE 312."
  },
  {
    "course_code": "CSE 431",
    "course_title": "Introduction to Theory of ComputationCoursePrerequisite:\u00c2\u00a0CSE 312."
  },
  {
    "course_code": "CSE 440",
    "course_title": "Introduction to HCI: User Interface Design, Prototyping, and EvaluationCoursePrerequisite:\u00c2\u00a0CSE 332."
  },
  {
    "course_code": "CSE 442",
    "course_title": "Data VisualizationCoursePrerequisite:\u00c2\u00a0CSE 332."
  },
  {
    "course_code": "CSE 444",
    "course_title": "Database Systems InternalsCoursePrerequisite:\u00c2\u00a0CSE 332; and either CSE 344 or CSE 414."
  },
  {
    "course_code": "CSE 446",
    "course_title": "CSE 440"
  },
  {
    "course_code": "CSE 447",
    "course_title": "Natural Language ProcessingCoursePrerequisite:\u00c2\u00a0CSE 312 and CSE 332."
  },
  {
    "course_code": "CSE 451",
    "course_title": "Introduction to Operating SystemsCoursePrerequisite:\u00c2\u00a0CSE 351; CSE 332; CSE 333."
  },
  {
    "course_code": "CSE 452",
    "course_title": "Introduction to Distributed SystemsCoursePrerequisite:\u00c2\u00a0CSE 332 and CSE 333."
  },
  {
    "course_code": "CSE 455",
    "course_title": "Computer VisionCoursePrerequisite:\u00c2\u00a0CSE 333; CSE 332."
  },
  {
    "course_code": "CSE 457",
    "course_title": "Computer GraphicsCoursePrerequisite:\u00c2\u00a0CSE 333; CSE 332."
  },
  {
    "course_code": "CSE 460",
    "course_title": "Animation CapstoneCoursePrerequisite:\u00c2\u00a0CSE 458, CSE 459."
  },
  {
    "course_code": "CSE 461",
    "course_title": "Introduction to Computer-Communication NetworksCoursePrerequisite:\u00c2\u00a0Either CSE 326 or CSE 332; either CSE 303 or CSE 333."
  },
  {
    "course_code": "CSE 469",
    "course_title": "Computer Architecture ICoursePrerequisite:\u00c2\u00a0Either E E 271 or CSE 369; and either CSE 123 or CSE 143."
  },
  {
    "course_code": "CSE 473",
    "course_title": "Introduction to Artificial IntelligenceCoursePrerequisite:\u00c2\u00a0CSE 312 and CSE 332."
  },
  {
    "course_code": "CSE 474",
    "course_title": "Introduction to Embedded SystemsCoursePrerequisite:\u00c2\u00a0CSE 123 or CSE 143"
  },
  {
    "course_code": "CSE 475",
    "course_title": "Embedded Systems CapstoneCoursePrerequisite:\u00c2\u00a0E E 271 or CSE 369; and E E 472 or CSE 474/E E 474."
  },
  {
    "course_code": "CSE 478",
    "course_title": "Autonomous RoboticsCoursePrerequisite:\u00c2\u00a0CSE 332."
  },
  {
    "course_code": "CSE 480",
    "course_title": "Computer Ethics SeminarCourse"
  },
  {
    "course_code": "CSE 481",
    "course_title": "Capstone Software DesignCoursePrerequisite:\u00c2\u00a0CSE 312; CSE 332; CSE 351; and either CSE 331, CSE 333, or CSE 369."
  },
  {
    "course_code": "CSE 482",
    "course_title": "Capstone Software Design to Empower Underserved PopulationsCoursePrerequisite:\u00c2\u00a0CSE 332; CSE 351; either CSE 331 or CSE 352."
  },
  {
    "course_code": "CSE 484",
    "course_title": "Computer SecurityCoursePrerequisite:\u00c2\u00a0CSE 332; CSE 351."
  },
  {
    "course_code": "CSE 490",
    "course_title": "Special Topics in Computer Science and EngineeringCourse"
  },
  {
    "course_code": "CSE 492",
    "course_title": "Undergraduate SeminarCourse"
  },
  {
    "course_code": "CSE 493",
    "course_title": "Advanced Special Topics in Computer Science and EngineeringCourse"
  },
  {
    "course_code": "CSE 495",
    "course_title": "Project PracticumCourse"
  },
  {
    "course_code": "CSE 496",
    "course_title": "Honors Undergraduate ResearchCourse"
  },
  {
    "course_code": "CSE 498",
    "course_title": "Undergraduate ResearchCourse"
  },
  {
    "course_code": "CSE 499",
    "course_title": "Reading and ResearchCourse"
  },
  {
    "course_code": "CSE 503",
    "course_title": "Software EngineeringCourse"
  },
  {
    "course_code": "CSE 510",
    "course_title": "Advanced Topics in Human-Computer InteractionCourse"
  },
  {
    "course_code": "HCDE 210",
    "course_title": "Explorations in Human Centered Design"
  },
  {
    "course_code": "HCDE 308",
    "course_title": "Visual Communication in Human Centered Design and Engineering"
  },
  {
    "course_code": "HCDE 498",
    "course_title": "Advanced Special Topics"
  },
  {
    "course_code": "HCDE 532",
    "course_title": "Web Design Studio"
  },
  {
    "course_code": "HCDE 298",
    "course_title": "Introductory Special Topics"
  },
  {
    "course_code": "HCDE 300",
    "course_title": "Foundations of Human Centered Design and Engineering"
  },
  {
    "course_code": "HCDE 301",
    "course_title": "Advanced Communication in HCDE"
  },
  {
    "course_code": "HCDE 302",
    "course_title": "Foundations of Human Centered Design I"
  },
  {
    "course_code": "HCDE 303",
    "course_title": "Foundations of Human Centered Design II"
  },
  {
    "course_code": "HCDE 310",
    "course_title": "Interactive Systems Design and Technology"
  },
  {
    "course_code": "HCDE 313",
    "course_title": "Introduction to User Research"
  },
  {
    "course_code": "HCDE 315",
    "course_title": "Inclusive Design and Engineering"
  },
  {
    "course_code": "HCDE 316",
    "course_title": "Sustainable Design"
  },
  {
    "course_code": "HCDE 318",
    "course_title": "Introduction to User-Centered Design"
  },
  {
    "course_code": "HCDE 321",
    "course_title": "Professional Portfolio"
  },
  {
    "course_code": "HCDE 322",
    "course_title": "Organizational Teamwork"
  },
  {
    "course_code": "HCDE 351",
    "course_title": "User Experience Prototyping Techniques"
  },
  {
    "course_code": "HCDE 398",
    "course_title": "Special Topics"
  },
  {
    "course_code": "HCDE 410",
    "course_title": "Human Data Interaction"
  },
  {
    "course_code": "HCDE 411",
    "course_title": "Information Visualization"
  },
  {
    "course_code": "HCDE 412",
    "course_title": "Qualitative Research Methods in Human Centered Design and Engineering"
  },
  {
    "course_code": "HCDE 417",
    "course_title": "Usability Research Techniques"
  },
  {
    "course_code": "HCDE 418",
    "course_title": "Advanced Projects in Human Centered Design and Engineering"
  },
  {
    "course_code": "HCDE 419",
    "course_title": "Concepts in Human-Computer Interaction"
  },
  {
    "course_code": "HCDE 438",
    "course_title": "Web Technologies"
  },
  {
    "course_code": "HCDE 439",
    "course_title": "Physical Computing"
  },
  {
    "course_code": "HCDE 440",
    "course_title": "Advanced Physical Computing"
  },
  {
    "course_code": "HCDE 485",
    "course_title": "Material and Cultural Bias in Algorithmic Systems"
  },
  {
    "course_code": "HCDE 492",
    "course_title": "Capstone Planning"
  },
  {
    "course_code": "HCDE 493",
    "course_title": "Senior Capstone"
  },
  {
    "course_code": "HCDE 494",
    "course_title": "Independent Study in Human Centered Design and Engineering"
  },
  {
    "course_code": "HCDE 496",
    "course_title": "Directed Research in Human Centered Design and Engineering"
  },
  {
    "course_code": "HCDE 497",
    "course_title": "Study Abroad: Human Centered Design and Engineering"
  },
  {
    "course_code": "HCDE 499",
    "course_title": "Individual Research"
  },
  {
    "course_code": "HCDE 501",
    "course_title": "Theoretical Foundations of Human Centered Design and Engineering"
  },
  {
    "course_code": "HCDE 502",
    "course_title": "Empirical Traditions in Human Centered Design and Engineering"
  },
  {
    "course_code": "HCDE 503",
    "course_title": "Navigating Design in Organizations"
  },
  {
    "course_code": "HCDE 505",
    "course_title": "Computer-Assisted Communication"
  },
  {
    "course_code": "HCDE 508",
    "course_title": "Visual Communication"
  },
  {
    "course_code": "HCDE 509",
    "course_title": "Writing the Scientific Article"
  },
  {
    "course_code": "HCDE 510",
    "course_title": "Information Design"
  },
  {
    "course_code": "HCDE 511",
    "course_title": "Information Visualization"
  },
  {
    "course_code": "HCDE 512",
    "course_title": "International User Experience and Communication"
  },
  {
    "course_code": "HCDE 513",
    "course_title": "Globalization and Localization Management"
  },
  {
    "course_code": "HCDE 514",
    "course_title": "Strategies for International Product Management"
  },
  {
    "course_code": "HCDE 515",
    "course_title": "Accessibility and Inclusive Design"
  },
  {
    "course_code": "HCDE 516",
    "course_title": "Experimental Research Methods"
  },
  {
    "course_code": "HCDE 517",
    "course_title": "Usability Studies"
  },
  {
    "course_code": "HCDE 518",
    "course_title": "User-Centered Design"
  },
  {
    "course_code": "HCDE 519",
    "course_title": "Qualitative Research Methods"
  },
  {
    "course_code": "HCDE 520",
    "course_title": "Design and Management of Complex Systems"
  },
  {
    "course_code": "HCDE 521",
    "course_title": "Seminar: Current Issues in Human Centered Design and Engineering"
  },
  {
    "course_code": "HCDE 523",
    "course_title": "Design Use Build"
  },
  {
    "course_code": "HCDE 524",
    "course_title": "Programming Concepts in HCDE"
  },
  {
    "course_code": "HCDE 525",
    "course_title": "Emerging Issues in Human Centered Design and Engineering"
  },
  {
    "course_code": "HCDE 526",
    "course_title": "Video Prototyping"
  },
  {
    "course_code": "HCDE 529",
    "course_title": "Service Design"
  },
  {
    "course_code": "HCDE 530",
    "course_title": "Computational Concepts in HCDE"
  },
  {
    "course_code": "HCDE 533",
    "course_title": "Digital Fabrication"
  },
  {
    "course_code": "HCDE 534",
    "course_title": "Designing a Human Centered Venture"
  },
  {
    "course_code": "HCDE 536",
    "course_title": "Interaction Design and Prototyping"
  },
  {
    "course_code": "HCDE 537",
    "course_title": "User-Centered Web Design"
  },
  {
    "course_code": "HCDE 538",
    "course_title": "Designing for Behavior Change"
  },
  {
    "course_code": "HCDE 539",
    "course_title": "Physical Computing and Prototyping"
  },
  {
    "course_code": "HCDE 541",
    "course_title": "Introduction to PhD Studies in HCDE"
  },
  {
    "course_code": "HCDE 542",
    "course_title": "Theoretical Foundations in Human Centered Design and Engineering"
  },
  {
    "course_code": "HCDE 543",
    "course_title": "Empirical Traditions in Human Centered Design and Engineering"
  },
  {
    "course_code": "HCDE 544",
    "course_title": "Experimental and Quasi-Experimental Research Methods"
  },
  {
    "course_code": "HCDE 545",
    "course_title": "Qualitative Research Methods"
  },
  {
    "course_code": "HCDE 546",
    "course_title": "Design Thinking"
  },
  {
    "course_code": "HCDE 547",
    "course_title": "Academic Research Seminar"
  },
  {
    "course_code": "HCDE 548",
    "course_title": "Advanced Topics in Human Centered Design and Engineering"
  },
  {
    "course_code": "HCDE 554",
    "course_title": "Engineering as Research and Inquiry"
  },
  {
    "course_code": "HCDE 555",
    "course_title": "Design as Research and Inquiry"
  },
  {
    "course_code": "HCDE 592",
    "course_title": "Capstone Planning"
  },
  {
    "course_code": "HCDE 593",
    "course_title": "Capstone"
  },
  {
    "course_code": "HCDE 596",
    "course_title": "Directed Research in Human Centered Design and Engineering"
  },
  {
    "course_code": "HCDE 597",
    "course_title": "Approaches to Teaching Technical Communication"
  },
  {
    "course_code": "HCDE 598",
    "course_title": "Special Topics"
  },
  {
    "course_code": "HCDE 599",
    "course_title": "Special Projects"
  },
  {
    "course_code": "HCDE 600",
    "course_title": "Independent Study or Research"
  },
  {
    "course_code": "HCDE 601",
    "course_title": "Internship"
  },
  {
    "course_code": "HCDE 700",
    "course_title": "Master's Thesis"
  },
  {
    "course_code": "HCDE 800",
    "course_title": "Doctoral Dissertation"
  }
];

export default courses;