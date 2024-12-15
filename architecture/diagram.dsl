workspace {

    model {
        user = person "User" {
            description "A job seeker managing their job applications."
        }

        jobTracker = softwareSystem "Job Tracker" {
            description "A system to manage job applications, resumes, and cover letters."

            cli = container "CLI Interface" {
                description "CLI interface for user interactions."
                technology "Python (Typer)"
            }

            appLayer = container "Application Layer" {
                description "Implements use cases and business rules."
                technology "Python"
            }

            domainLayer = container "Domain Layer" {
                description "Core business entities and rules."
                technology "Python"
            }

            infraLayer = container "Infrastructure Layer" {
                description "Implements data persistence and external API integration."
                technology "Python, PostgreSQL, External APIs"
            }

            postgresDB = container "PostgreSQL Database" {
                description "Stores job, resume, application, and cover letter data."
                technology "PostgreSQL"
            }

            llmAPI = container "External LLM API" {
                description "Performs job analysis and generates recommendations."
                technology "External API"
            }

            user -> cli "Uses"
            cli -> appLayer "Executes commands"
            appLayer -> domainLayer "Executes business logic"
            appLayer -> infraLayer "Accesses repositories and APIs"
            infraLayer -> postgresDB "Reads/Writes data"
            infraLayer -> llmAPI "Requests job analysis and recommendations"
        }
    }

    views {
        systemContext jobTracker {
            description "System context diagram for the Job Tracker."
            include *
            autolayout lr
        }

        container jobTracker {
            description "Container diagram for the Job Tracker."
            include *
            autolayout lr
        }
    }

}
