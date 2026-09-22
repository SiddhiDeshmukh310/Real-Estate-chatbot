import React from "react";
import Header from "./components/Header";
import ChatInterface from "./components/ChatInterface";

export default function App() {
  return (
    <>
      <Header />
      <main className="app-container">
        <ChatInterface />
      </main>
    </>
  );
}

