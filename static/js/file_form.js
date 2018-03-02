        //show image? seleted by user for file form field
        jQuery(window).on("load", function () {
            var inputs = document.querySelectorAll('.inputfile');
            Array.prototype.forEach.call(inputs, function (input) {
                var label = input.nextElementSibling,
                    labelVal = label.innerHTML;

                input.addEventListener('change', function (e) {
                    console.log(1);
                    var fileName = '';
                    if (this.files && this.files.length > 1) {
                        fileName = this.files.length + " files selected";

                    }
                    else
                        fileName = e.target.value.split('\\').pop();

                    if (fileName)
                        label.querySelector('span').innerHTML = fileName
                    else
                        label.innerHTML = labelVal;
                });
            });
        });