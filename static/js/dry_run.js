"use strict";

(function initDryRun() {
  function getAcceptedCount() {
    return document.querySelectorAll(".proposal-row:has(.cancel-btn-form)").length;
  }

  function updateAcceptAllButton() {
    var acceptAllBtn = document.getElementById("accept-all-btn");
    var runRenamesBtn = document.getElementById("run-renames-btn");
    var acceptedCount = getAcceptedCount();
    var totalProposals = document.querySelectorAll(".proposal-row").length;

    if (acceptAllBtn) {
      if (acceptedCount === totalProposals && totalProposals > 0) {
        acceptAllBtn.className = "btn btn-secondary";
        acceptAllBtn.disabled = true;
        acceptAllBtn.textContent = "Accepted";
      } else {
        acceptAllBtn.className = "btn btn-outline-warning";
        acceptAllBtn.disabled = false;
        acceptAllBtn.textContent = "Accept All";
      }
    }

    if (runRenamesBtn) {
      if (acceptedCount > 0) {
        runRenamesBtn.className = "btn btn-warning";
        runRenamesBtn.disabled = false;
      } else {
        runRenamesBtn.className = "btn btn-outline-warning disabled";
        runRenamesBtn.disabled = true;
      }
    }
  }

  function handleAcceptClick(event, movieId) {
    var row = document.querySelector('[data-movie-id="' + movieId + '"]');
    if (!row) return;

    var acceptBtn = row.querySelector(".accept-btn");
    var skipBtn = row.querySelector(".skip-btn");
    var cancelBtn = row.querySelector(".cancel-btn");

    if (acceptBtn) {
      acceptBtn.className = "btn btn-sm btn-success disabled";
      acceptBtn.disabled = true;
      acceptBtn.textContent = "Accepted";
    }
    if (skipBtn) skipBtn.style.display = "none";
    if (cancelBtn) cancelBtn.style.display = "inline-flex";

    updateAcceptAllButton();
  }

  function handleCancelClick(event, movieId) {
    var row = document.querySelector('[data-movie-id="' + movieId + '"]');
    if (!row) return;

    var acceptBtn = row.querySelector(".accept-btn");
    var skipBtn = row.querySelector(".skip-btn");
    var cancelBtn = row.querySelector(".cancel-btn");

    if (acceptBtn) {
      acceptBtn.className = "btn btn-sm btn-primary";
      acceptBtn.disabled = false;
      acceptBtn.textContent = "Accept";
    }
    if (skipBtn) skipBtn.style.display = "inline-flex";
    if (cancelBtn) cancelBtn.style.display = "none";

    updateAcceptAllButton();
  }

  document.querySelectorAll(".accept-btn-form").forEach(function(form) {
    form.addEventListener("submit", function(event) {
      var movieId = form.dataset.movieId;
      handleAcceptClick(event, movieId);
    });
  });

  document.querySelectorAll(".cancel-btn-form").forEach(function(form) {
    form.addEventListener("submit", function(event) {
      var movieId = form.dataset.movieId;
      handleCancelClick(event, movieId);
    });
  });

  var acceptAllForm = document.getElementById("accept-all-form");
  if (acceptAllForm) {
    acceptAllForm.addEventListener("submit", function() {
      setTimeout(updateAcceptAllButton, 100);
    });
  }

  updateAcceptAllButton();
})();
