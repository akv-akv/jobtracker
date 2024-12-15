workspace "jobtracker" "Jobtracker workspace" {

    !identifiers hierarchical

    model {
        user = person "User"
        jobtracker = softwareSystem "Jobtracker" {
            wa = container "Web Application"
            db = container "Database Schema" {
                tags "Database"
            }
        }

        user -> jobtracker.wa "Uses"
        jobtracker.wa -> jobtracker.db "Reads from and writes to"
    }

    views {
        systemContext jobtracker "Diagram1" {
            include *
            autolayout lr
        }

        container jobtracker "Diagram2" {
            include *
            autolayout lr
        }
    }

}
