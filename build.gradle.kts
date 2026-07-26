plugins {
    base
}

tasks.register("assembleDebug") {
    doLast {
        println("Dummy assembleDebug task for non-Android web project")
    }
}

tasks.register("lint") {
    doLast {
        println("Dummy lint task for non-Android web project")
    }
}
