async function encode() {
    if (!validateEncodeParameters()) {
        return;
    }

    disableControls();

    const inputImageFile = document.getElementById("input-image").files[0];
    const inputImage = await fileToBase64(inputImageFile);
    const outputImageName = document.getElementById("output-image").value;
    const outputFormat = document.getElementById("output-format").value;
    const outputImage = outputImageName + '.' + outputFormat;
    const dataInput = document.getElementById("data-input").value;
    const dataFile = document.getElementById("data-file").files[0];
    let data = null;
    let fileName = null;
    if (dataFile) {
        data = await fileToBase64(dataFile);
        fileName = dataFile.name;
    } else {
        data = dataInput;
    }
    const pattern = getPattern();

    const result = await eel.encode_data(inputImage, outputImage, data, fileName, pattern)();
    document.getElementById("console-output").innerHTML = result;

    enableControls();
}

function validateEncodeParameters() {
    const inputImageFile = document.getElementById("input-image").files[0];
    const outputImageName = document.getElementById("output-image").value;

    if (!inputImageFile) {
        document.getElementById("console-output").innerHTML = "Error: Please select an input image.";
        return false;
    }

    if (!outputImageName) {
        document.getElementById("console-output").innerHTML = "Error: Please enter an output image name.";
        return false;
    }

    return true;
}

async function decode() {
    if (!validateDecodeParameters()) {
        return;
    }

    disableControls();

    const inputImageFile = document.getElementById("input-image").files[0];
    const inputImage = await fileToBase64(inputImageFile);
    const pattern = getPattern();
    const enforceProvidedPattern = document.getElementById("enforce-provided-pattern").checked;
    const dataLength = document.getElementById("data-length").value;

    const result = await eel.decode_data(inputImage, pattern, enforceProvidedPattern, dataLength)();
    document.getElementById("console-output").innerHTML = result;

    enableControls();
}

function validateDecodeParameters() {
    const inputImageFile = document.getElementById("input-image").files[0];

    if (!inputImageFile) {
        document.getElementById("console-output").innerHTML = "Error: Please select an input image.";
        return false;
    }

    return true;
}

function fileToBase64(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = () => resolve(reader.result);
        reader.onerror = error => reject(error);
        reader.readAsDataURL(file);
    });
}

function getPattern() {
    const headerEnabled = document.getElementById("header-enabled").checked;
    const headerWriteDataSize = document.getElementById("header-write-data-size").checked;
    const headerWritePattern = document.getElementById("header-write-pattern").checked;
    const headerChannels = $("#header-channels").val();
    const headerPosition = document.getElementById("header-position").querySelector(".active").dataset.value;
    const headerBitFrequency = document.getElementById("header-bit-frequency").value;
    const headerByteSpacing = document.getElementById("header-byte-spacing").value;
    const headerRepetitiveRedundancy = document.getElementById("header-repetitive-redundancy").value;
    const headerAdvancedRedundancy = document.getElementById("header-advanced-redundancy").querySelector(".active").dataset.value;
    const headerAdvancedRedundancyCorrectionFactor = document.getElementById("header-advanced-redundancy-correction-factor").value;

    const offset = document.getElementById("offset").value;
    const channels = $("#channels").val();
    const bitFrequency = document.getElementById("bit-frequency").value;
    const byteSpacing = document.getElementById("byte-spacing").value;
    const hashCheck = document.getElementById("hash-check").value;
    const compression = document.getElementById("compression").value;
    const compressionStrength = document.getElementById("compression-strength").value;
    const advancedRedundancy = document.getElementById("advanced-redundancy").querySelector(".active").dataset.value;
    const advancedRedundancyCorrectionFactor = document.getElementById("advanced-redundancy-correction-factor").value;
    const repetitiveRedundancy = document.getElementById("repetitive-redundancy").value;
    const repetitiveRedundancyMode = document.getElementById("repetitive-redundancy-mode").querySelector(".active").dataset.value;

    return {
        "header": {
            "enabled": headerEnabled,
            "write_data_size": headerWriteDataSize,
            "write_pattern": headerWritePattern,
            "channels": headerChannels,
            "position": headerPosition,
            "bit_frequency": headerBitFrequency,
            "byte_spacing": headerByteSpacing,
            "repetitive_redundancy": headerRepetitiveRedundancy,
            "advanced_redundancy": headerAdvancedRedundancy,
            "advanced_redundancy_correction_factor": headerAdvancedRedundancyCorrectionFactor
        },
        "offset": offset,
        "channels": channels,
        "bit_frequency": bitFrequency,
        "byte_spacing": byteSpacing,
        "hash_check": hashCheck,
        "compression": compression,
        "compression_strength": compressionStrength,
        "advanced_redundancy": advancedRedundancy,
        "advanced_redundancy_correction_factor": advancedRedundancyCorrectionFactor,
        "repetitive_redundancy": repetitiveRedundancy,
        "repetitive_redundancy_mode": repetitiveRedundancyMode
    };
}

document.addEventListener('DOMContentLoaded', function () {
    var triggerTabList = [].slice.call(document.querySelectorAll('#data-tab, #pattern-tab, #process-tab'))
    triggerTabList.forEach(function (triggerEl) {
        var tabTrigger = new bootstrap.Tab(triggerEl)
        triggerEl.addEventListener('click', function () {
            tabTrigger.show()
        })
    })
})

eel.expose(encode_data);
eel.expose(decode_data);

function selectOption(button) {
    $(button).siblings().removeClass("active");
    $(button).addClass("active");
}

function disableControls() {
    const controls = document.querySelectorAll("button, input, select");
    controls.forEach(control => {
        control.disabled = true;
    });
}

function enableControls() {
    const controls = document.querySelectorAll("button, input, select");
    controls.forEach(control => {
        control.disabled = false;
    });
}
