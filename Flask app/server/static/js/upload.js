$(document).ready(function() {
    let filesToUpload = [];
    let files2Upload = []; // New variable to store an array copy of the files
    
    function removePrefix(str, prefix) {
        if (str.startsWith(prefix)) {
            return str.slice(prefix.length);
        }
        return str;
    }

    function handleFiles(files) {
        filesToUpload = files; // Keep the original FileList
        files2Upload = Array.from(files); // Convert FileList to array for easier manipulation

        $("#imagePreview").empty(); // Clear any existing previews
        $("#dropzoneText").addClass("hidden"); // Hide the text
        $("#imagePreview").css("display", "flex"); // Show the image preview container

        for (let i = 0; i < files.length; i++) {
            let file = files[i];
            let reader = new FileReader();

            reader.onload = function(e) {
                let img = $("<img>").attr("src", e.target.result).addClass("img-thumbnail").css({
                    "max-width": "150px",
                    "max-height": "150px"
                });
                $("#imagePreview").append(img);
            };

            reader.readAsDataURL(file);
        }
    }

    // Handle file drop
    $("#dropzone").on("dragover", function(e) {
        e.preventDefault();
        e.stopPropagation();
        $(this).addClass("dragover");
    });

    $("#dropzone").on("dragleave", function(e) {
        e.preventDefault();
        e.stopPropagation();
        $(this).removeClass("dragover");
    });

    $("#dropzone").on("drop", function(e) {
        e.preventDefault();
        e.stopPropagation();
        $(this).removeClass("dragover");

        let files = e.originalEvent.dataTransfer.files;
        handleFiles(files);
    });

    // Handle click to select files
    $("#dropzone").on("click", function() {
        let fileInput = $("<input>").attr({
            type: "file",
            multiple: "multiple",
            accept: "image/*"
        });
        fileInput.on("change", function(e) {
            let files = e.target.files;
            handleFiles(files);
        });
        fileInput.click();
    });

    // Handle clustering
    $("#clusterBtn").on("click", function() {
        if (filesToUpload.length === 0) {
            alert("Please select some images first.");
            return;
        }

        let formData = new FormData();
        for (let i = 0; i < filesToUpload.length; i++) {
            formData.append("files[]", filesToUpload[i]);
        }

        // Upload files
        $.ajax({
            url: "/upload",
            type: "POST",
            data: formData,
            contentType: false,
            processData: false,
            success: function(uploadResponse) {
                console.log("Upload response:", uploadResponse);

                // Perform clustering
                $.ajax({
                    url: "/cluster",
                    type: "POST",
                    data: JSON.stringify(uploadResponse.file_paths), // Sending only file paths for clustering
                    contentType: "application/json",
                    success: function(clusterResponse) {
                        console.log("Cluster response:", clusterResponse);
                        displayClusters(clusterResponse);
                    },
                    error: function(error) {
                        console.error("Cluster error:", error);
                        alert("Error during clustering.");
                    }
                });
            },
            error: function(error) {
                console.error("Upload error:", error);
                alert("Error during upload.");
            }
        });
    });

    function displayClusters(data) {
        $("#response").empty();
        
        // Get unique cluster labels
        let uniqueLabels = [...new Set(data.cluster_labels)];
        
        for (let i = 0; i < uniqueLabels.length; i++) {
            let clusterLabel = uniqueLabels[i];
            
            // Filter image names that belong to the current cluster label
            let clusterImages = data.image_names.filter((name, index) => clusterLabel === data.cluster_labels[index]);
    
            if (clusterImages.length > 0) {
                let clusterHtml = `<div class="cluster" id="cluster${i}">
                                       <h2>Group ${clusterLabel}</h2>
                                       <div class="cluster-images">`;
    
                // Add images to cluster
                clusterImages.forEach((imageName) => {
                    // Find the file in files2Upload by matching the name case-insensitively
                    let file = files2Upload.find(file => removePrefix(file.name.toLowerCase(), "_") === imageName.toLowerCase());
                    if (file) {
                        // Create an object URL for the file
                        let imageUrl = URL.createObjectURL(file);
                        clusterHtml += `<img src="${imageUrl}" alt="${imageName}" class="img-thumbnail" style="max-width: 150px; max-height: 150px;">`;
                    } else {
                        // In case the file is not found in files2Upload, show an error
                        clusterHtml += `<p>Image ${imageName} not found in the upload list.</p>`;
                    }
                });
    
                clusterHtml += `</div></div>`;
                $("#response").append(clusterHtml);
            }
        }
    }
    
});
