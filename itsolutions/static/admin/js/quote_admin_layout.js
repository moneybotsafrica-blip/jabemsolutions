(function () {
    "use strict";

    function placeTermsAfterItems() {
        const termsFieldset = Array.from(document.querySelectorAll("fieldset.module"))
            .find((fieldset) => fieldset.querySelector("h2")?.textContent.trim() === "Terms and totals");
        const itemsInline = document.querySelector("#items-group");

        if (termsFieldset && itemsInline) {
            itemsInline.insertAdjacentElement("afterend", termsFieldset);
        }
    }

    document.addEventListener("DOMContentLoaded", placeTermsAfterItems);
}());
