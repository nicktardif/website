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
