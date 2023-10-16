export const ide_en = {
    server_was_overloaded_try_again: "The server was probably overloaded 😥 Please try again!",
    no_live_output_result_to_follow: "Live output not possible, result will follow shortly...",
    compilation_successful: "Compilation successful 🎉",
    compilation_started: "Compilation started... 🛠",
    program_running: "Program running...",
    program_testing: "Program testing 📝➡️✅ please wait...",
    no_executables_found: "🔎 Unfortunately, no executables were found. Please compile first ⚙",
    program_exited_without_output: "Program exited (successfully, but without output)! ✔",
    program_exited_probably_with_error: "Program exited (probably with an error)! ❌",
    security_error: "💥🙈 There seems to have been a security error while testing your program. Apparently, your program tried to execute things that are not allowed. Please correct this first.\nIf the problem persists, you should contact your teacher.",
    computation_time_exceeded: "❌ Program was terminated prematurely! The computation time has probably expired. Do you have an infinite loop somewhere?",
    all_tests_passed: "All tests passed 🎉🤩\n\nYou can now try to \"beautify\" your source code ;-)",
    no_test_passed: "Oops 🧐 Apparently, not a single test was passed! Maybe the output above will help you find the errors 🤗",
    error_during_testing: "💥🙈 There seems to have been an error while testing your program. Please try again!\nFirst, make sure your program can be executed.\nIf the problem persists, you should contact your teacher.",
    test_aborted: "❌ The test was aborted by the user.",
    x_percent_of_tests_passed: "You passed {percent}% of the tests. Maybe the output above will help you pass the remaining tests as well 🤗",
    stopped_by_user: "\nProgram was stopped by the user! ✔",
    error_loading_project: "Error loading project. Please go back or reload.",
    error_on_saving: "Error on saving!",
    couldnt_rename_file: "File could not be renamed.",
    file_rename_successful: "File successfully renamed.",
    error_saving_project_description: "Error saving project description.",
    error_project_name_empty: "Project name must not be empty!",
    project_not_existing_or_no_access: "Project does not exist, or you do not have access to it!",
    error_creating_homework: "Error creating assignment!",
    homework_created_successfully: "Assignment created successfully.",
    file_created_successfully: "File created successfully.",
    error_creating_file: "Error creating file.",
    error_deleting_file: "Error deleting file.",
    error_reseting_homework_progress: "Error resetting assignment progress!",
    error_stopping_program: "Program could not be stopped!",
    changing_template_may_lead_to_inconsistencies: "Changing the template may lead to inconsistencies!",
    description_of_inconsistencies_when_changing_template: "You are currently editing the <u>template</u> of an assignment! If you make changes to the <b>code</b> and save them, this can lead to inconsistencies among the different students: <ul><li>For students who have already started working on this assignment, your changes will <b>not arrive</b> until they delete their progress and start the assignment again.</li><li>For students who have not yet started working on this assignment, the first time they open it they will always use the latest code of this template.</li></ul>Changes to the <b>title or project description</b>, on the other hand, are not a problem and can be changed at any time and will be updated for the students when they reload the IDE.",
    save_changes_before_closing: "Do you want to save the changes before closing?",
    add_new_file: "Add new file",
    description_new_file: "Enter the new file name for the file. Remember to include the file extension (typically <code>.java</code>)! <br> <br>If you want to create a folder, you must also specify a file within the new folder. <br><br><b><u>Example:</u></b><br>If you want to create the folder \"<code>new</code>\", you must also specify a file within the folder (e.g. <code>MyClass.java</code>). Therefore, enter the full file name as <code>new/MyClass.java</code>.",
    filename_is_invalid: "Filename is invalid (contains spaces or the name already exists)!",
    question_delete_file: "Delete file?",
    ask_delete_file_x: "Do you really want to delete the file {0}?",
    delete_folder: "Delete folder",
    delete_folder_description: "Unfortunately, folders cannot be deleted directly. However, you can delete all the contents of the folder, and the folder will be deleted automatically.",
    rename_folder: "Rename folder",
    rename_folder_description: "Unfortunately, folders cannot be renamed directly. However, you can rename all the contents of the folder, and a new folder with the new name will be created automatically. The old folder will be deleted automatically.<br><br><u><b>Example:</b></u><br>If you have a folder named <code>old</code> containing two files named <code>First.java</code> and <code>Second.java</code>, with full names <code>old/First.java</code> and <code>old/Second.java</code>, renaming the files to <code>new/First.java</code> and <code>new/Second.java</code> is equivalent to renaming the folder from <code>old</code> to <code>new</code>.",
    rename_file: "Rename file",
    rename_file_description: "Enter the new name for the file {0}. Remember to include the file extension (typically {1})!",
    rename_file_invalid: "Filename is invalid (contains spaces or the name already exists)!",
    create_assignment: "Create assignment",
    create_assignment_description_1: "⚠️<b>Important:</b> The configuration of a project should be fully completed <b>before</b> creating an assignment from it. After this step, changes should be avoided, as students may otherwise work on different versions.",
    create_assignment_description_2: "When creating an assignment, the <b>current state</b> of your project is copied and saved as a template for the students in the background. After creation, further changes to this private project by you will <b>not</b> be visible in the assignment for the students. E.g. you can safely delete this private project afterwards, and the assignment will still exist. <b>Important:</b> Students cannot change or rename the entry point (= class with main method)!",
    assignment_already_created: "An assignment has already been created from this project for the following courses:",
    choose_course: "Choose course",
    create_course_in_usermanagement: "You must first create a course in the user management (ideally with students)!",
    create_assignment: "Create assignment",
    question_restart_assignment: "Restart assignment?",
    restart_assignment_description: "Do you want to delete your previous progress and start again from a \"clean\" project?",
    new_file: "New file",
    restart_assignment: "Restart assignment",
    ctrl_s: "Ctrl + S",
    ctrl_1: "Ctrl + 1",
    ctrl_2: "Ctrl + 2",
    ctrl_3: "Ctrl + 3",
    compile: "Compile",
    execute: "Execute",
    test: "Test",
    placeholder_for_input: "Input (press Enter to send)",
    set_as_entry_point: "Set as entry point",
    error_main_class_not_found: "No main method was found in the main/initial class (with 🏠). Make sure that a method with the following signature exists there:\npublic static void main(String[] args)",
    tooltip_entry_point: "The main/initial class of the program, which must also contain the main method.",
    edit_computation_time: "Edit computation time",
    success_setting_computation_time: "Computation time successfully set.",
    error_setting_computation_time: "Error setting computation time.",
}