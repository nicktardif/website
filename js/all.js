window.addEventListener('load', function(event) {
  addImages('food');
  addImages('recent');
  addImages('all');

  galleryId = 'my-gallery';
  displayGallery(galleryId);

  setMenuLeftPadding();
});
