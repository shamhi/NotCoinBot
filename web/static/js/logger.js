const updateLogs = async () => {
    const logsBlock = document.querySelector('.logs');

    try {
        const response = await fetch('/api/v1/getLogs', {
            method: 'GET'
        });

        if (response.ok) {
            const data = await response.text();
            const logs = data.split('\n');

            logs.reverse().forEach(log => {
                const logElement = document.createElement('ol');
                logElement.textContent = log;
                logsBlock.appendChild(logElement);
            });
        }
    } catch (error) {
        console.error("Error while receiving data:", error);
    }
};
