        //show image, seleted by user for file form field
        jQuery(window).on("load", function () {


            var inputs = document.querySelectorAll('.inputfile');
            Array.prototype.forEach.call(inputs, function (input) {
                var label = input.nextElementSibling,
                    labelVal = label.innerHTML;

                input.addEventListener('change', function (e) {
                    var fileName = '';
                    if (this.files && this.files.length > 1) {
                        fileName = this.files.length + " выбрано";

                    }
                    else
                        fileName = e.target.value.split('\\').pop();

                    if (fileName) {
                        console.log(fileName);
                        $('span.photo_text').html(fileName);
                    }
                    else
                        label.innerHTML = labelVal;
                });
            });


        });