import { parse } from 'content-disposition-attachment';

const convert_button = document.querySelector(".convert-button");
const url_input = document.querySelector(".url-input");
const progress_bar = document.querySelector("#progress-bar");
const progress_bar_block = document.querySelector("#progress-bar-block");
const error_message = document.querySelector("#error-message");
const error_message_block = document.querySelector("#error-message-block");
const postprocessing_block = document.querySelector("#loading-block");
const postprocessing_loading = document.querySelector("#loading");

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

function show_postprocessing() {
    postprocessing_block.style.display = "block"
}

function hide_postprocessing() {
    postprocessing_block.style.display = "none"
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
            return res.json();
        })
        .then((data) => {
            const current_download_id = data.id;
            setTimeout(() => download_update(current_download_id), 1000);
        })
        .catch((err) => {
            reset_progress();
            show_error(err);
        });
}

function download_delete(id) {
    fetch(`http://localhost:8000/download/${id}`, {
        method: "DELETE",
    });
}

function download_transfer(id) {
    fetch(`http://localhost:8000/download/${id}`, {
        method: "GET",
    })
        .then((res) => {
            const url = window.URL.createObjectURL(new Blob([res.data]));
            const link = document.createElement("a");
            const filename = parse(res.headers.get("content-disposition"));
            link.href = url;
            console.log(filename.filename);
            link.setAttribute("download", filename.filename);
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);

            download_delete(id);
        })
        .catch((err) => {
            reset_progress();
            show_error(err);
        });
}

function handle_update(id, download_record) {
    switch (download_record.status) {
        case "ERROR":
            reset_progress();
            hide_postprocessing();
            show_error("Unidentified error returned by 'yt-dlp'.");
            break;

        case "IN_PROGRESS":
            hide_postprocessing();
            progress_bar.value = download_record.progress;
            setTimeout(() => download_update(id), 1000);
            break;

        case "POSTPROCESSING":
            show_postprocessing();
            progress_bar.value = download_record.progress;
            setTimeout(() => download_update(id), 1000);
            break;

        case "FINISHED":
            console.log("Download finished on backend. Transferring!");
            progress_bar.value = download_record.progress;
            hide_postprocessing();
            download_transfer(id);
            break;

        default:
            reset_progress()
            hide_postprocessing();
            show_error(`Invalid status ${download_record.status}`);
            break;
    }
}

function download_update(id) {
    fetch(`http://localhost:8000/download/${id}/status`, {
        method: "GET",
    })
        .then((res) => {
            return res.json();
        })
        .then((data) => {
            handle_update(id, data);
        })
        .catch((err) => {
            reset_progress();
            show_error(err);
        });
}