filters = []

/*
 * Replace all SVG images with inline SVG
 */
function svgToInline() {
  jQuery('img.svg').each(function(){
    var $img = jQuery(this);
    var imgID = $img.attr('id');
    var imgClass = $img.attr('class');
    var imgURL = $img.attr('src');

    jQuery.get(imgURL, function(data) {
      // Get the SVG tag, ignore the rest
      var $svg = jQuery(data).find('svg');

      // Add replaced image's ID to the new SVG
      if(typeof imgID !== 'undefined') {
        $svg = $svg.attr('id', imgID);
      }
      // Add replaced image's classes to the new SVG
      if(typeof imgClass !== 'undefined') {
        $svg = $svg.attr('class', imgClass+' replaced-svg');
      }

      // Remove any invalid XML tags as per http://validator.w3.org
      $svg = $svg.removeAttr('xmlns:a');

      // Check if the viewport is set, if the viewport is not set the SVG wont't scale.
      if(!$svg.attr('viewBox') && $svg.attr('height') && $svg.attr('width')) {
        $svg.attr('viewBox', '0 0 ' + $svg.attr('height') + ' ' + $svg.attr('width'))
      }

      // Replace image with new SVG
      $img.replaceWith($svg);

    }, 'xml');
  });
};

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
                item.msrc = linkEl.children[0].getAttribute('src');
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

            getThumbBoundsFn: function(index) {
                // See Options -> getThumbBoundsFn section of documentation for more info
                var thumbnail = items[index].el.getElementsByTagName('img')[0], // find thumbnail
                    pageYScroll = window.pageYOffset || document.documentElement.scrollTop,
                    rect = thumbnail.getBoundingClientRect(); 

                return {x:rect.left, y:rect.top + pageYScroll, w:rect.width};
            },
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

function addImages(gallerySelector) {
  var json_file = 'images/images.json'
  var request = new XMLHttpRequest();
  request.open("GET", json_file, false);
  request.send(null)
  var images_json_dict = JSON.parse(request.responseText); 

  var images_json_array = []

  for(var key in images_json_dict) {
    images_json_array.push(images_json_dict[key])
  }

  images_json_array.sort(compareDate);

  images_json_array.forEach(function(element) {
    size = getSize(element['full_image_path']);
    full_image_path = element['full_image_path'];
    thumbnail_path = element['thumbnail_path'];
    caption = element['caption'];

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
            '<img src="' + thumbnail_path + '" itemprop="thumbnail" alt="Image description" />' +
          '</a>' +
          '<figcaption itemprop="caption description">' + caption + '</figcaption>' +
        '</figure>';
    $(gallerySelector).append(html);
  });

  initPhotoSwipeFromDOM(gallerySelector);
};

window.onload = function() {
  gallerySelector = '.my-gallery';
  addImages(gallerySelector);
  svgToInline();

  $(document).on('click','#travel-filter',function() {
    if ($(this).hasClass('active')) {
      index = filters.indexOf('travel');
      if(index > -1) {
        filters.splice(index, 1);
      }
      $(this).removeClass('active');
    } else {
      filters.push('travel');  
      $(this).addClass('active');
    }
    $(gallerySelector).empty();
    addImages(gallerySelector);
  });

  $(document).on('click','#food-filter',function() {
    if ($(this).hasClass('active')) {
      index = filters.indexOf('food');
      if(index > -1) {
        filters.splice(index, 1);
      }
      $(this).removeClass('active');
    } else {
      filters.push('food');  
      $(this).addClass('active');
    }
    $(gallerySelector).empty();
    addImages(gallerySelector);
  });

  $(document).on('click','#plant-filter',function() {
    if ($(this).hasClass('active')) {
      index = filters.indexOf('plant');
      if(index > -1) {
        filters.splice(index, 1);
      }
      $(this).removeClass('active');
    } else {
      filters.push('plant');  
      $(this).addClass('active');
    }
    $(gallerySelector).empty();
    addImages(gallerySelector);
  });

  $(document).on('click','#people-filter',function() {
    if ($(this).hasClass('active')) {
      index = filters.indexOf('people');
      if(index > -1) {
        filters.splice(index, 1);
      }
      $(this).removeClass('active');
    } else {
      filters.push('people');  
      $(this).addClass('active');
    }
    $(gallerySelector).empty();
    addImages(gallerySelector);
  });

  $(document).on('click','#reset-filter',function() {
    $(document).find('#travel-filter').removeClass('active')
    $(document).find('#food-filter').removeClass('active')
    $(document).find('#plant-filter').removeClass('active')
    $(document).find('#people-filter').removeClass('active')
    filters = []

    $(gallerySelector).empty();
    addImages(gallerySelector);
  });
}
