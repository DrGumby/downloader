const convert_button = document.querySelector(".convert-button");
const url_input = document.querySelector(".url-input");
const progress_bar = document.querySelector("#progress-bar");
const progress_bar_block = document.querySelector("#progress-bar-block");
const error_message = document.querySelector("#error-message");
const error_message_block = document.querySelector("#error-message-block");

convert_button.addEventListener("click", () => {
    console.log(`Sending url: ${url_input.value}`);
    download_start(url_input.value);
});

function init_progress() {
    progress_bar_block.style.display = "block";
    progress_bar.value = 0;
}

function reset_progress() {
    progress_bar.value = 0;
    progress_bar_block.style.display = "none";
}

function show_error(msg) {
    error_message_block.style.display = "block";
    error_message.innerHTML = msg;
    console.log(msg);
}

function reset_error() {
    error_message_block.style.display = "none";
    error_message.innerHTML = "";
}

function download_start(url) {
    fetch(`http://localhost:8000/download/?start=${url}`, {
        method: "POST",
    })
        .then((res) => {
            reset_error();
            init_progress();
        })
        .catch((err) => {
            reset_progress();
            show_error(err);
        });
}
