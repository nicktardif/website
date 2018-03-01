filters = []
images_json_array = []

function initPhotoSwipeFromDOM(gallerySelector) {

    // parse slide data (url, title, size ...) from DOM elements 
    // (children of gallerySelector)
    var parseThumbnailElements = function(el) {
        var thumbElements = el.childNodes,
            numNodes = thumbElements.length,
            items = [],
            figureEl,
            linkEl,
            size,
            item;

        for(var i = 0; i < numNodes; i++) {

            figureEl = thumbElements[i]; // <figure> element

            // include only element nodes 
            if(figureEl.nodeType !== 1) {
                continue;
            }

            linkEl = figureEl.children[0]; // <a> element
            size = linkEl.getAttribute('data-size').split('x');

            // create slide object
            item = {
                src: linkEl.getAttribute('href'),
                w: parseInt(size[0], 10),
                h: parseInt(size[1], 10)
            };

            if(figureEl.children.length > 1) {
                // <figcaption> content
                item.title = figureEl.children[1].innerHTML; 
            }

            if(linkEl.children.length > 0) {
                // <img> thumbnail element, retrieving thumbnail url
                //item.msrc = linkEl.children[0].getAttribute('src');
            } 

            item.el = figureEl; // save link to element for getThumbBoundsFn
            items.push(item);
        }
        return items;
    };

    // find nearest parent element
    var closest = function closest(el, fn) {
        return el && ( fn(el) ? el : closest(el.parentNode, fn) );
    };

    // triggers when user clicks on thumbnail
    var onThumbnailsClick = function(e) {
        e = e || window.event;
        e.preventDefault ? e.preventDefault() : e.returnValue = false;

        var eTarget = e.target || e.srcElement;

        // find root element of slide
        var clickedListItem = closest(eTarget, function(el) {
            return (el.tagName && el.tagName.toUpperCase() === 'FIGURE');
        });

        if(!clickedListItem) {
            return;
        }

        // find index of clicked item by looping through all child nodes
        // alternatively, you may define index via data- attribute
        var clickedGallery = clickedListItem.parentNode,
            childNodes = clickedListItem.parentNode.childNodes,
            numChildNodes = childNodes.length,
            nodeIndex = 0,
            index;

        for (var i = 0; i < numChildNodes; i++) {
            if(childNodes[i].nodeType !== 1) { 
                continue; 
            }

            if(childNodes[i] === clickedListItem) {
                index = nodeIndex;
                break;
            }
            nodeIndex++;
        }

        if(index >= 0) {
            // open PhotoSwipe if valid index found
            openPhotoSwipe( index, clickedGallery );
        }
        return false;
    };

    // parse picture index and gallery index from URL (#&pid=1&gid=2)
    var photoswipeParseHash = function() {
        var hash = window.location.hash.substring(1),
        params = {};

        if(hash.length < 5) {
            return params;
        }

        var vars = hash.split('&');
        for (var i = 0; i < vars.length; i++) {
            if(!vars[i]) {
                continue;
            }
            var pair = vars[i].split('=');  
            if(pair.length < 2) {
                continue;
            }           
            params[pair[0]] = pair[1];
        }

        if(params.gid) {
            params.gid = parseInt(params.gid, 10);
        }

        return params;
    };

    var openPhotoSwipe = function(index, galleryElement, disableAnimation, fromURL) {
        var pswpElement = document.querySelectorAll('.pswp')[0],
            gallery,
            options,
            items;

        items = parseThumbnailElements(galleryElement);

        // define options (if needed)
        options = {

            // define gallery index (for URL)
            galleryUID: galleryElement.getAttribute('data-pswp-uid'),

            //getThumbBoundsFn: function(index) {
            //    // See Options -> getThumbBoundsFn section of documentation for more info
            //    var thumbnail = items[index].el.getElementsByTagName('img')[0], // find thumbnail
            //        pageYScroll = window.pageYOffset || document.documentElement.scrollTop,
            //        rect = thumbnail.getBoundingClientRect();

            //    return {x:rect.left, y:rect.top + pageYScroll, w:rect.width};
            //},
            getThumbBoundsFn: false,
            showHideOpacity: true

        };

        // PhotoSwipe opened from URL
        if(fromURL) {
            if(options.galleryPIDs) {
                // parse real index when custom PIDs are used 
                // http://photoswipe.com/documentation/faq.html#custom-pid-in-url
                for(var j = 0; j < items.length; j++) {
                    if(items[j].pid == index) {
                        options.index = j;
                        break;
                    }
                }
            } else {
                // in URL indexes start from 1
                options.index = parseInt(index, 10) - 1;
            }
        } else {
            options.index = parseInt(index, 10);
        }

        // exit if index not found
        if( isNaN(options.index) ) {
            return;
        }

        if(disableAnimation) {
            options.showAnimationDuration = 0;
        }

        // Pass data to PhotoSwipe and initialize it
        gallery = new PhotoSwipe( pswpElement, PhotoSwipeUI_Default, items, options);
        gallery.init();
    };

    // loop through all gallery elements and bind events
    var galleryElements = document.querySelectorAll( gallerySelector );

    for(var i = 0, l = galleryElements.length; i < l; i++) {
        galleryElements[i].setAttribute('data-pswp-uid', i+1);
        galleryElements[i].onclick = onThumbnailsClick;
    }

    // Parse URL and open gallery if it contains #&pid=3&gid=1
    var hashData = photoswipeParseHash();
    if(hashData.pid && hashData.gid) {
        openPhotoSwipe( hashData.pid ,  galleryElements[ hashData.gid - 1 ], true, true );
    }
};

function baseName(str)
{
  var base = new String(str).substring(str.lastIndexOf('/') + 1); 
  if(base.lastIndexOf(".") != -1)       
    base = base.substring(0, base.lastIndexOf("."));
  return base;
}

function getSize(filename) {
  basename = baseName(filename)
  dimension_string = basename.split('_').pop()
  return dimension_string
};

function compareDate(a,b) {
  if (a['date'] < b['date'])
    return 1;
  if (a['date'] > b['date'])
    return -1;
  return 0;
}

function addImages(category) {
  var json_file = 'images/downsampled/' + category + '.json'
  var request = new XMLHttpRequest();
  request.open("GET", json_file, false);
  request.send(null)
  var images_json_dict = JSON.parse(request.responseText); 

  for(var idx in images_json_dict) {
    image = images_json_dict[idx]
    image['css_category'] = category
    images_json_array.push(image)
  }
}

function displayGallery(galleryId) {
  images_json_array.sort(compareDate);

  previous_image_basename = ''

  images_json_array.forEach(function(element) {
    size = getSize(element['full_image_path']);
    full_image_path = element['full_image_path'];
    thumbnail_path = element['thumbnail_path'];
    caption = element['caption'];
    css_category = element['css_category'];
    image_basename = baseName(full_image_path);
    thumb_basename = baseName(thumbnail_path)
    sprite_class = 'sprite-' + css_category + '-' + thumb_basename

    // Don't display the same image twice
    // This works because the data is already sorted
    if(image_basename === previous_image_basename) {
      return;
    }
    previous_image_basename = image_basename

    if(filters.length != 0) {
      found_match = false;
      element['tags'].forEach(function(tag) {
        if(filters.indexOf(tag) >= 0) {
          found_match = true;
        }
      });
      if(!found_match) {
        return;
      }
    }

    var html = '' +
        '<figure itemprop="associatedMedia" itemscope itemtype="http://schema.org/ImageObject">' +
          '<a href="' + full_image_path + '" itemprop="contentUrl" data-size="' + size + '">' +
            '<div class="' + sprite_class + '" itemprop="thumbnail" />' +
          '</a>' +
          '<figcaption itemprop="caption description">' + caption + '</figcaption>' +
        '</figure>';
    var gallery = document.getElementById(galleryId);
    gallery.insertAdjacentHTML('beforeend', html);
  });

  initPhotoSwipeFromDOM('#' + galleryId);
}

/* Set the width of the side navigation to 250px */
function openNav() {
  document.getElementById("sidenav").style.width = "250px";
}

/* Set the width of the side navigation to 0 */
function closeNav() {
  document.getElementById("sidenav").style.width = "0";
}

function getPageTopLeft(el) {
  var rect = el.getBoundingClientRect();
  var docEl = document.documentElement;
  return {
    left: rect.left + (window.pageXOffset || docEl.scrollLeft || 0),
    top: rect.top + (window.pageYOffset || docEl.scrollTop || 0)
  };
}

function setMenuLeftPadding() {
  firstImg = document.getElementById(galleryId).getElementsByTagName('figure')[0];
  topLeft = getPageTopLeft(firstImg);
  document.getElementById("opennav").style.paddingLeft = topLeft.left + "px";
}

window.addEventListener('load', function(event) {
  document.getElementById("closenavbtn").onclick = function() { 
    closeNav(); 
  };
  document.getElementById("opennav").onclick = function() { 
    openNav(); 
  };
});

window.addEventListener('resize', function(event) {
  setMenuLeftPadding();
});
