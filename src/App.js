import { useState } from "react";
import "./App.css";

function App() {
    const [inputValue, setInputValue] = useState("");
    const [chatHistory, setChatHistory] = useState([]);

    const sendMessage = async () => {
        if (!inputValue.trim()) return;

        const updatedHistory = [...chatHistory, { sender: "player", text: inputValue }];
        setChatHistory(updatedHistory);

        try {
            const res = await fetch(`http://localhost:8000/${encodeURIComponent(inputValue)}`);
            const data = await res.json();
            console.log(res);
            setChatHistory([...updatedHistory, { sender: "npc", text: data.message }]);
        } catch (err) {
            setChatHistory([...updatedHistory, { sender: "npc", text: "Ошибка соединения с сервером" }]);
        }

        setInputValue("");
    };

    return (
        <div className="App">
            <div className="container">
                <div className="chat">
                    {chatHistory.map((msg, idx) => (
                        <div key={idx}>
                            {msg.sender === "player" ? "> " : "NPC: "}
                            {msg.text}
                        </div>
                    ))}
                </div>
                <div>
                    <input
                        value={inputValue}
                        onChange={(e) => setInputValue(e.target.value)}
                        onKeyDown={(e) => e.key === "Enter" && sendMessage()}
                    />
                    <button onClick={sendMessage}>OK</button>
                </div>
            </div>
        </div>
    );
}

export default App;
