
let logsIntervalId;

const clickOn = async () => {
    try {
        const response = await fetch('/api/v1/clickOn', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        if (response.ok) {
            const data = await response.json();
            if (data.ok === true) {
                const clickButton = document.querySelector('.click-button');

                clickButton.innerHTML = clickButton.innerHTML.replace("Click On", "Click Off")
                clickButton.onclick = clickOff
                clickButton.style.setProperty('--click-button-background', 'linear-gradient(-30deg, #3d0b0b 50%, #2b0808 50%)');
                clickButton.style.setProperty('--click-button-color', '#f7d4d4');
                clickButton.style.setProperty('--click-button-before-background-color', '#ad8585');
                clickButton.style.setProperty('--button-animated-span-background', 'linear-gradient(to left, rgba(43, 8, 8, 0), #d92626)');
            } else {
                alert("Try again");
            }
        }

        logsIntervalId = setInterval(updateLogs, 2000)
    } catch (error) {
        console.error('Error:', error);
    }
};


const clickOff = async () => {
    try {
        const response = await fetch('/api/v1/clickOff', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        if (response.ok) {
            const data = await response.json();
            if (data.ok === true) {
                const clickButton = document.querySelector('.click-button');

                clickButton.innerHTML = clickButton.innerHTML.replace("Click Off", "Click On");
                clickButton.onclick = clickOn
                clickButton.style.setProperty('--click-button-background', 'linear-gradient(-30deg, #0b3d0b 50%, #082b08 50%)');
                clickButton.style.setProperty('--click-button-color', '#d4f7d4');
                clickButton.style.setProperty('--click-button-before-background-color', '#85ad85');
                clickButton.style.setProperty('--button-animated-span-background', 'linear-gradient(to left, rgba(8, 43, 8, 0), #26d926)');
            } else {
                alert("Try again");
            }
        }

        clearInterval(logsIntervalId)
    } catch (error) {
        console.error('Error:', error);
    }
};
