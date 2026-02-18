// some scripts

// jquery ready start
$(document).ready(function() {
	// jQuery code


    /* ///////////////////////////////////////

    THESE FOLLOWING SCRIPTS ONLY FOR BASIC USAGE, 
    For sliders, interactions and other

    */ ///////////////////////////////////////
    

	//////////////////////// Prevent closing from click inside dropdown
    $(document).on('click', '.dropdown-menu', function (e) {
      e.stopPropagation();
    });


    $('.js-check :radio').change(function () {
        var check_attr_name = $(this).attr('name');
        if ($(this).is(':checked')) {
            $('input[name='+ check_attr_name +']').closest('.js-check').removeClass('active');
            $(this).closest('.js-check').addClass('active');
           // item.find('.radio').find('span').text('Add');

        } else {
            item.removeClass('active');
            // item.find('.radio').find('span').text('Unselect');
        }
    });


    $('.js-check :checkbox').change(function () {
        var check_attr_name = $(this).attr('name');
        if ($(this).is(':checked')) {
            $(this).closest('.js-check').addClass('active');
           // item.find('.radio').find('span').text('Add');
        } else {
            $(this).closest('.js-check').removeClass('active');
            // item.find('.radio').find('span').text('Unselect');
        }
    });



	//////////////////////// Bootstrap tooltip
	if($('[data-toggle="tooltip"]').length>0) {  // check if element exists
		$('[data-toggle="tooltip"]').tooltip()
	} // end if



    /* ======================================
       PRODUCTION-READY STAR RATING
       Half-star support (0.5, 1, 1.5, ... 5)
       Cumulative highlighting with active states
       ====================================== */
    
    var StarRating = {
        
        init: function() {
            var self = this;
            var $ratingContainers = $('.rate');
            
            if ($ratingContainers.length === 0) return;
            
            $ratingContainers.each(function() {
                var $container = $(this);
                var $labels = $container.find('label');
                var $inputs = $container.find('input[type="radio"]');
                
                // Load any previously selected rating
                self.restoreActiveState($container, $labels);
                
                // Bind mouse events for hover preview
                $labels.on('mouseenter', function() {
                    self.handleMouseEnter($container, $labels);
                });
                
                $labels.on('mousemove', function(e) {
                    self.handleMouseMove($(this), $container, $labels, e);
                });
                
                $container.on('mouseleave', function() {
                    self.handleMouseLeave($container, $labels);
                });
                
                // Bind click event to labels
                $labels.on('click', function(e) {
                    e.preventDefault();
                    e.stopPropagation();
                    self.handleClick($(this), $container, $labels);
                });
                
                // Keyboard support (arrow keys)
                $inputs.on('keydown', function(e) {
                    if (e.keyCode === 37 || e.keyCode === 39) { // Left/Right arrow
                        e.preventDefault();
                        var $this = $(this);
                        var index = $inputs.index($this);
                        var direction = e.keyCode === 39 ? 1 : -1;
                        var newIndex = Math.max(0, Math.min($inputs.length - 1, index + direction));
                        $inputs.eq(newIndex).click();
                    }
                });
            });
        },
        
        /**
         * Get which star (including half-stars) the user is hovering over
         * Accounts for flex-direction: row-reverse
         * Returns: 0-9 (index)
         */
        getStarIndex: function($label, $container) {
            var $labels = $container.find('label');
            var index = $labels.index($label);
            // Reverse index because of flex-direction: row-reverse
            return $labels.length - 1 - index;
        },
        
        /**
         * Get the rating value from a label (0.5, 1, 1.5, ... 5)
         */
        getRatingValue: function($label, $container) {
            var $input = $label.prev('input[type="radio"]');
            return parseFloat($input.val());
        },
        
        /**
         * Clear all hover classes from labels
         */
        clearHover: function($labels) {
            $labels.removeClass('hover');
        },
        
        /**
         * Clear all active classes and re-sync with checked input
         */
        syncActiveState: function($container, $labels) {
            var $checked = $container.find('input:checked');
            var $allLabels = $labels;
            var self = this;
            
            // Clear all active classes first
            $allLabels.removeClass('active');
            
            // If a radio is checked, apply active class to that label and all to the right
            if ($checked.length > 0) {
                var checkedIndex = $allLabels.index($checked.next('label'));
                if (checkedIndex >= 0) {
                    // Apply active class to this label and all after it
                    $allLabels.each(function(i) {
                        if (i >= checkedIndex) {
                            $(this).addClass('active');
                        }
                    });
                }
            }
        },
        
        /**
         * Restore active state on page load
         */
        restoreActiveState: function($container, $labels) {
            this.syncActiveState($container, $labels);
        },
        
        /**
         * Apply hover state to preview the rating (including half-stars)
         */
        applyHover: function($label, $container, $labels) {
            var starIndex = this.getStarIndex($label, $container);
            
            // Clear all hover classes first
            this.clearHover($labels);
            
            // Add hover to this label and all after it
            $labels.each(function(i) {
                var reverseIndex = $labels.length - 1 - i;
                if (reverseIndex <= starIndex) {
                    $(this).addClass('hover');
                }
            });
        },
        
        handleMouseEnter: function($container, $labels) {
            // Clear hover state on mouse enter for a fresh start
            this.clearHover($labels);
        },
        
        handleMouseMove: function($label, $container, $labels, e) {
            // Apply hover effect to show rating preview
            this.applyHover($label, $container, $labels);
        },
        
        handleMouseLeave: function($container, $labels) {
            // Remove all hover classes when leaving
            this.clearHover($labels);
        },
        
        /**
         * Handle click - select the rating and make it permanent
         */
        handleClick: function($label, $container, $labels) {
            var ratingValue = this.getRatingValue($label, $container);
            
            // Find the corresponding radio input
            var $input = $label.prev('input[type="radio"]');
            if ($input.length === 0) {
                console.error('Rating input not found!');
                return;
            }
            
            // Check the radio button
            $input.prop('checked', true);
            
            // Verify the value was set correctly
            console.log('Radio input value: ' + $input.val());
            console.log('Radio input checked: ' + $input.is(':checked'));
            
            // Trigger change event for form submission
            $input.trigger('change');
            
            // Sync the active state to show permanent selection
            this.syncActiveState($container, $labels);
            
            // Apply hover for immediate visual feedback
            this.applyHover($label, $container, $labels);
            
            // Log for debugging
            console.log('Star rating selected: ' + ratingValue + ' stars');
            
            // Verify the form data
            var $form = $container.closest('form');
            if ($form.length) {
                console.log('Form found. Rating value in form: ' + $form.find('input[name="rating"]').val());
            } else {
                console.warn('No form found for rating submission!');
            }
        }
    };
    
    // Initialize star rating when document is ready
    StarRating.init();
    
    // Add form submission handler to verify rating value
    $(document).on('submit', 'form', function(e) {
        var $form = $(this);
        var ratingValue = $form.find('input[name="rating"]:checked').val();
        
        if (ratingValue) {
            console.log('=== FORM SUBMISSION DEBUG ===');
            console.log('Selected Rating Value: ' + ratingValue);
            console.log('Rating Type: ' + typeof ratingValue);
            console.log('Rating as Float: ' + parseFloat(ratingValue));
            console.log('All form data:');
            console.log($form.serialize());
            console.log('============================');
        }
    });

    
}); 
// jquery end

// setTimeout(function(){
//   $('#message').fadeOut('slow')
// }, 4000)



