function deleteImage(objButton) {
	imageId = objButton.value;
	var xhr = new XMLHttpRequest();
	xhr.open("DELETE", "/api/v1/images/" + imageId, true);
	xhr.send();
}

function deleteAlbum(objButton) {
	albumId = objButton.value;
	var xhr = new XMLHttpRequest();
	xhr.open("DELETE", "/api/v1/albums/" + albumId, true);
	xhr.send();
}

function removeImageFromAlbum(objButton) {
	var imageId = objButton.dataset.imageId;
	var albumId = objButton.dataset.albumId;
	var xhr = new XMLHttpRequest();
	xhr.open("DELETE", "/api/v1/albums/" + albumId + "/images/" + imageId, true);
	xhr.send();
	// TODO: Provide notification if the call was successful
	// https://developer.mozilla.org/en-US/docs/Web/API/XMLHttpRequest/response
}

function addImageToAlbum(objButton) {
	var imageId = objButton.dataset.imageId;
	var albumId = document.getElementById("image_new_album_dropdown").value;
	var xhr = new XMLHttpRequest();
	xhr.open("POST", "/api/v1/albums/" + albumId + "/images/" + imageId, true);
	xhr.send();
	// TODO: Provide notification if the call was successful
	// https://developer.mozilla.org/en-US/docs/Web/API/XMLHttpRequest/response
}

function updateImageCaption(objButton) {
	var imageId = objButton.dataset.imageId;
	var caption = document.getElementById("image_caption").value;
	let data = {}
	data['caption'] = caption;

	let xhr = new XMLHttpRequest();
	xhr.open("PATCH", "/api/v1/images/" + imageId, true);
	xhr.setRequestHeader("Content-Type", "application/json");
	xhr.send(JSON.stringify(data));
	// TODO: Provide notification if the call was successful
	// https://developer.mozilla.org/en-US/docs/Web/API/XMLHttpRequest/response
}

function updateImageLocation(objButton) {
	var imageId = objButton.dataset.imageId;
	var location = document.getElementById("image_location").value;
	let data = {}
	data['location'] = location;

	let xhr = new XMLHttpRequest();
	xhr.open("PATCH", "/api/v1/images/" + imageId, true);
	xhr.setRequestHeader("Content-Type", "application/json");
	xhr.send(JSON.stringify(data));
	// TODO: Provide notification if the call was successful
	// https://developer.mozilla.org/en-US/docs/Web/API/XMLHttpRequest/response
}

function updateImageDate(objButton) {
	var imageId = objButton.dataset.imageId;
	var date = document.getElementById("image_date").value;
	let data = {}
	data['date'] = date;
	// NOTE: 2011-11-04 00:05:23 is the valid ISO format

	let xhr = new XMLHttpRequest();
	xhr.open("PATCH", "/api/v1/images/" + imageId, true);
	xhr.setRequestHeader("Content-Type", "application/json");
	xhr.send(JSON.stringify(data));
	// TODO: Provide notification if the call was successful
	// https://developer.mozilla.org/en-US/docs/Web/API/XMLHttpRequest/response
}

function removeAlbumFromPortfolio(objButton) {
	var albumId = objButton.dataset.albumId;
	var portfolioId = objButton.dataset.portfolioId;
	var xhr = new XMLHttpRequest();
	xhr.open("DELETE", "/api/v1/portfolios/" + portfolioId + "/albums/" + albumId, true);
	xhr.send();
	// TODO: Provide notification if the call was successful
	// https://developer.mozilla.org/en-US/docs/Web/API/XMLHttpRequest/response
}

function addAlbumToPortfolio(objButton) {
	var albumId = objButton.dataset.albumId;
	var portfolioId = document.getElementById("album_new_portfolio_dropdown").value;
	var xhr = new XMLHttpRequest();
	xhr.open("POST", "/api/v1/portfolios/" + portfolioId + "/albums/" + albumId, true);
	xhr.send();
	// TODO: Provide notification if the call was successful
	// https://developer.mozilla.org/en-US/docs/Web/API/XMLHttpRequest/response
}

function setAsPrimaryAlbum(objButton) {
	var portfolioId = objButton.dataset.portfolioId;
	var primaryAlbumId = document.getElementById("portfolio_new_primary_album_dropdown").value;
	let data = {}
	data['primary_album_id'] = primaryAlbumId;

	let xhr = new XMLHttpRequest();
	xhr.open("PATCH", "/api/v1/portfolios/" + portfolioId, true);
	xhr.setRequestHeader("Content-Type", "application/json");
	xhr.send(JSON.stringify(data));
	// TODO: Provide notification if the call was successful
	// https://developer.mozilla.org/en-US/docs/Web/API/XMLHttpRequest/response
}

function updatePortfolioName(objButton) {
	var portfolioId = objButton.dataset.portfolioId;
	var name = document.getElementById("portfolio_name").value;
	let data = {}
	data['name'] = name;

	let xhr = new XMLHttpRequest();
	xhr.open("PATCH", "/api/v1/portfolios/" + portfolioId, true);
	xhr.setRequestHeader("Content-Type", "application/json");
	xhr.send(JSON.stringify(data));
	// TODO: Provide notification if the call was successful
	// https://developer.mozilla.org/en-US/docs/Web/API/XMLHttpRequest/response
}

function deletePortfolio(objButton) {
	var portfolioId = objButton.dataset.portfolioId;
	let xhr = new XMLHttpRequest();
	xhr.open("DELETE", "/api/v1/portfolios/" + portfolioId, true);
	xhr.send();
	// TODO: Provide notification if the call was successful
	// https://developer.mozilla.org/en-US/docs/Web/API/XMLHttpRequest/response
}

function generateWebsite(objButton) {
	var portfolioId = objButton.dataset.portfolioId;
	let xhr = new XMLHttpRequest();
	xhr.open("POST", "/api/v1/portfolios/" + portfolioId + "/generate", true);
	xhr.send();
	// TODO: Provide notification if the call was successful
	// https://developer.mozilla.org/en-US/docs/Web/API/XMLHttpRequest/response
}

function updateAlbumName(objButton) {
	var albumId = objButton.dataset.albumId;
	var name = document.getElementById("album_name").value;
	let data = {}
	data['name'] = name;

	let xhr = new XMLHttpRequest();
	xhr.open("PATCH", "/api/v1/albums/" + albumId, true);
	xhr.setRequestHeader("Content-Type", "application/json");
	xhr.send(JSON.stringify(data));
	// TODO: Provide notification if the call was successful
	// https://developer.mozilla.org/en-US/docs/Web/API/XMLHttpRequest/response
}
