function deleteImage(objButton) {
	imageId = objButton.value;
	var xhr = new XMLHttpRequest();
	xhr.open("DELETE", "/api/v1/images/" + imageId, true);
	xhr.send();
}
