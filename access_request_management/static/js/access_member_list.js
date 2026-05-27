const CONFIG = window.MEMBER_LIST_CONFIG || {};
const T = CONFIG.translations || {};
const CSRF = CONFIG.csrfToken || "";

let pendingAction = null;

function showModal(id) {
    const el = document.getElementById(id);
    if (!el) return;
    if (typeof bootstrap !== "undefined") {
        bootstrap.Modal.getOrCreateInstance(el).show();
    } else if (typeof $ !== "undefined") {
        $(el).modal("show");
    } else {
        el.style.display = "block";
        el.classList.add("show");
        document.body.classList.add("modal-open");
    }
}

function hideModal(id) {
    const el = document.getElementById(id);
    if (!el) return;
    if (typeof bootstrap !== "undefined") {
        const modal = bootstrap.Modal.getInstance(el);
        if (modal) modal.hide();
    } else if (typeof $ !== "undefined") {
        $(el).modal("hide");
    } else {
        el.style.display = "none";
        el.classList.remove("show");
        document.body.classList.remove("modal-open");
    }
}

function showToast(message, type = "success") {
    const container = document.getElementById("toast-container");
    const id = "toast-" + Date.now();
    const icon = type === "success" ? "mdi-check-circle" : "mdi-close-circle";
    const colorClass = type === "success" ? "text-success" : "text-danger";
    const html = `
      <div id="${id}" class="toast align-items-center border-0 shadow-sm" role="alert">
        <div class="d-flex align-items-center p-2">
          <i class="mdi ${icon} ${colorClass} me-2 fs-5"></i>
          <div class="toast-body py-0 px-1">${message}</div>
          <button type="button" class="btn-close ms-auto me-1" data-bs-dismiss="toast"></button>
        </div>
      </div>`;
    container.insertAdjacentHTML("beforeend", html);
    const toastEl = document.getElementById(id);
    if (typeof bootstrap !== "undefined") {
        const bsToast = bootstrap.Toast.getOrCreateInstance(toastEl, { delay: 4000 });
        bsToast.show();
        toastEl.addEventListener("hidden.bs.toast", () => toastEl.remove());
    } else {
        toastEl.style.display = "block";
        toastEl.classList.add("show");
        setTimeout(() => toastEl.remove(), 4000);
        toastEl.querySelector(".btn-close")?.addEventListener("click", () => toastEl.remove());
    }
}

function openConfirmModal({ pk, action, name, title, message, btnClass, btnLabel, iconClass, iconBg }) {
    pendingAction = { pk, action };
    document.getElementById("confirmModalTitle").textContent = title;
    document.getElementById("confirmModalBody").textContent = message;
    const iconWrap = document.getElementById("confirmModalIcon");
    iconWrap.className = `rounded-circle d-inline-flex align-items-center justify-content-center mb-3 ${iconBg}`;
    document.getElementById("confirmModalIconI").className = `mdi ${iconClass}`;
    const btn = document.getElementById("confirmActionBtn");
    btn.className = `btn btn-sm px-4 ${btnClass}`;
    btn.textContent = btnLabel;
    showModal("confirmActionModal");
}

function callPersonAction(pk, action) {
    const url = `/api/plugins/access_request_management/access-requests-person/${pk}/${action}/`;
    fetch(url, {
        method: "POST",
        headers: {
            "X-CSRFToken": CSRF,
            "Content-Type": "application/json",
        },
    })
    .then((res) => res.json())
    .then((data) => {
        hideModal("confirmActionModal");
        if (data.id) {
            showToast(T.success, "success");
            setTimeout(() => window.location.reload(), 1200);
        } else {
            showToast(data.detail || T.error, "danger");
        }
    })
    .catch(() => showToast(T.connectionError, "danger"));
}

document.getElementById("confirmActionBtn").addEventListener("click", function () {
    if (pendingAction) {
        callPersonAction(pendingAction.pk, pendingAction.action);
    }
});

document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll(".btn-verify").forEach((btn) => {
        btn.addEventListener("click", function () {
            const pk = this.dataset.pk;
            const name = this.dataset.name || "";
            openConfirmModal({
                pk, action: "verify", name,
                title: T.verifyMember,
                message: `${T.confirmVerify} "${name}"?`,
                btnClass: "btn-success",
                btnLabel: T.verify,
                iconClass: "mdi-shield-check",
                iconBg: "bg-success bg-opacity-10 text-success",
            });
        });
    });

    document.querySelectorAll(".btn-unverify").forEach((btn) => {
        btn.addEventListener("click", function () {
            const pk = this.dataset.pk;
            const name = this.dataset.name || "";
            openConfirmModal({
                pk, action: "unverified", name,
                title: T.unverifyMember,
                message: `${T.confirmUnverify} "${name}"?`,
                btnClass: "btn-danger",
                btnLabel: T.unverify,
                iconClass: "mdi-shield-off",
                iconBg: "bg-danger bg-opacity-10 text-danger",
            });
        });
    });
});