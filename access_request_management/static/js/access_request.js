(function () {

    function showToast(msg, type, callback) {
        const toast = document.getElementById('ar-toast');

        const icon =
            type === 'success'
                ? 'mdi-check-circle'
                : 'mdi-alert-circle';

        toast.className = 'show ' + type;

        toast.innerHTML = `
            <i class="mdi ${icon}" style="font-size:18px"></i>
            <span>${msg}</span>
        `;

        setTimeout(() => {
            toast.classList.remove('show');

            if (callback) {
                callback();
            }
        }, 2000);
    }

    function setLoading(btn, isLoading, loadingText, defaultHtml) {

        btn.disabled = isLoading;

        btn.innerHTML = isLoading
            ? `<span class="spinner"></span>${loadingText}`
            : defaultHtml;
    }

    async function handleFormSubmit(
        formId,
        buttonId,
        loadingText,
        successText,
        successMessage,
        defaultHtml
    ) {

        const form = document.getElementById(formId);

        if (!form) {
            return;
        }

        form.addEventListener("submit", async function (e) {

            e.preventDefault();

            const btn = document.getElementById(buttonId);

            const csrfToken =
                document.querySelector("[name=csrfmiddlewaretoken]").value;

            const url = form.dataset.url;

            setLoading(
                btn,
                true,
                loadingText,
                defaultHtml
            );

            try {

                const response = await fetch(url, {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "X-CSRFToken": csrfToken,
                    },
                    credentials: "same-origin"
                });

                const data = await response.json();

                if (!response.ok) {

                    showToast(
                        data.detail || data.error || "Request failed.",
                        "error"
                    );

                    setLoading(
                        btn,
                        false,
                        loadingText,
                        defaultHtml
                    );

                    return;
                }

                btn.innerHTML = successText;
                btn.disabled = true;

                showToast(successMessage, "success", () => {
                    location.reload();
                });

            } catch (error) {

                console.error(error);

                showToast(
                    "Unexpected error occurred.",
                    "error"
                );

                setLoading(
                    btn,
                    false,
                    loadingText,
                    defaultHtml
                );
            }
        });
    }

    handleFormSubmit(
        "submit-access-request-form",
        "btn-submit",
        "Sending...",
        '<i class="mdi mdi-check"></i>Sent',
        "Access request submitted successfully!",
        '<i class="mdi mdi-send"></i>Send'
    );

    handleFormSubmit(
        "confirm-access-request-form",
        "btn-confirm",
        "Confirming...",
        '<i class="mdi mdi-check"></i>Confirmed',
        "Access request confirmed successfully!",
        '<i class="mdi mdi-check-circle"></i>Confirm'
    );

})();