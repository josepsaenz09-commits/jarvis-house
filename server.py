import os
from flask import Flask, request, jsonify, render_template_string, Response
from openai import OpenAI

app = Flask(__name__)

client = OpenAI(
    api_key=os.environ.get("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)

HTML = r"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
    <meta name="theme-color" content="#05080e">
    <meta name="mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">

    <title>J.A.R.V.I.S.</title>

    <link rel="manifest" href="/manifest.json">
    <link rel="icon" href="/icon.svg" type="image/svg+xml">

    <style>
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }

        body {
            min-height: 100vh;
            background:
                radial-gradient(circle at center, #09202b 0%, #05080e 45%, #020408 100%);
            color: #d9fbff;
            font-family: Arial, sans-serif;
            overflow-x: hidden;
        }

        body::before {
            content: "";
            position: fixed;
            inset: 0;
            pointer-events: none;
            background:
                linear-gradient(rgba(0,234,255,.025) 1px, transparent 1px),
                linear-gradient(90deg, rgba(0,234,255,.025) 1px, transparent 1px);
            background-size: 35px 35px;
            z-index: -1;
        }

        #splash {
            position: fixed;
            inset: 0;
            z-index: 9999;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            background: #02060a;
            transition: opacity .8s ease, visibility .8s ease;
        }

        #splash.hide {
            opacity: 0;
            visibility: hidden;
        }

        .splash-title {
            color: #8feeff;
            font-size: clamp(35px, 9vw, 75px);
            font-weight: 700;
            letter-spacing: 9px;
            text-shadow:
                0 0 10px #00eaff,
                0 0 30px rgba(0,234,255,.7);
        }

        .splash-sub {
            margin-top: 12px;
            color: #55cfe3;
            letter-spacing: 5px;
            font-size: 12px;
        }

        .radar {
            width: 180px;
            height: 180px;
            margin: 35px 0;
            border: 1px solid rgba(0,234,255,.55);
            border-radius: 50%;
            position: relative;
            background:
                radial-gradient(circle, transparent 0 30%, rgba(0,234,255,.05) 31% 31.5%, transparent 32% 60%, rgba(0,234,255,.05) 61% 61.5%, transparent 62%);
            box-shadow: 0 0 30px rgba(0,234,255,.15);
        }

        .radar::before {
            content: "";
            position: absolute;
            left: 50%;
            top: 0;
            width: 1px;
            height: 100%;
            background: rgba(0,234,255,.25);
        }

        .radar::after {
            content: "";
            position: absolute;
            top: 50%;
            left: 0;
            width: 100%;
            height: 1px;
            background: rgba(0,234,255,.25);
        }

        .radar-line {
            position: absolute;
            width: 50%;
            height: 2px;
            left: 50%;
            top: 50%;
            transform-origin: left center;
            background: linear-gradient(90deg, #00eaff, transparent);
            animation: radar 2s linear infinite;
        }

        @keyframes radar {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
        }

        .progress {
            width: min(330px, 80vw);
            height: 4px;
            border-radius: 10px;
            overflow: hidden;
            background: #10222a;
        }

        #progressBar {
            width: 0%;
            height: 100%;
            background: #00eaff;
            box-shadow: 0 0 15px #00eaff;
            transition: width .25s linear;
        }

        #systemText {
            margin-top: 14px;
            font-size: 11px;
            color: #55cfe3;
            letter-spacing: 2px;
        }

        .app {
            width: min(1500px, 100%);
            min-height: 100vh;
            margin: auto;
            padding: 15px;
        }

        header {
            height: 65px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            border-bottom: 1px solid rgba(0,234,255,.25);
            margin-bottom: 15px;
        }

        .brand {
            font-size: 22px;
            font-weight: bold;
            letter-spacing: 4px;
            color: #a5f5ff;
            text-shadow: 0 0 12px rgba(0,234,255,.7);
        }

        .status {
            display: flex;
            align-items: center;
            gap: 8px;
            color: #65f6bd;
            font-size: 11px;
            letter-spacing: 2px;
        }

        .status-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: #65f6bd;
            box-shadow: 0 0 12px #65f6bd;
        }

        .grid {
            display: grid;
            grid-template-columns: 270px 1fr 270px;
            gap: 15px;
        }

        .panel {
            border: 1px solid rgba(0,234,255,.25);
            background: rgba(3,12,18,.72);
            box-shadow:
                inset 0 0 30px rgba(0,234,255,.025),
                0 0 20px rgba(0,0,0,.25);
            padding: 15px;
            position: relative;
        }

        .panel-title {
            font-size: 10px;
            color: #55cfe3;
            letter-spacing: 3px;
            margin-bottom: 15px;
        }

        .metric {
            margin-bottom: 18px;
        }

        .metric-row {
            display: flex;
            justify-content: space-between;
            font-size: 11px;
            margin-bottom: 7px;
        }

        .metric-value {
            color: #8feeff;
        }

        .bar {
            height: 5px;
            background: #10242c;
            overflow: hidden;
        }

        .bar span {
            display: block;
            height: 100%;
            width: 65%;
            background: #00eaff;
            box-shadow: 0 0 10px #00eaff;
        }

        .center {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            min-height: 650px;
        }

        .core {
            width: min(330px, 65vw);
            height: min(330px, 65vw);
            max-width: 330px;
            max-height: 330px;
            min-width: 220px;
            min-height: 220px;
            border-radius: 50%;
            border: 2px solid rgba(0,234,255,.6);
            display: flex;
            align-items: center;
            justify-content: center;
            position: relative;
            box-shadow:
                0 0 25px rgba(0,234,255,.25),
                inset 0 0 50px rgba(0,234,255,.08);
        }

        .core::before,
        .core::after {
            content: "";
            position: absolute;
            border-radius: 50%;
            border: 1px solid rgba(0,234,255,.35);
        }

        .core::before {
            inset: 25px;
            animation: spin 12s linear infinite;
        }

        .core::after {
            inset: 55px;
            border-style: dashed;
            animation: spinReverse 8s linear infinite;
        }

        @keyframes spin {
            to { transform: rotate(360deg); }
        }

        @keyframes spinReverse {
            to { transform: rotate(-360deg); }
        }

        .core-letter {
            font-size: 105px;
            font-weight: bold;
            color: #d7fbff;
            text-shadow:
                0 0 10px #00eaff,
                0 0 35px #00eaff;
            z-index: 2;
        }

        .core-label {
            margin-top: 25px;
            color: #67dbea;
            font-size: 12px;
            letter-spacing: 4px;
        }

        .command-button {
            margin-top: 22px;
            width: 75px;
            height: 75px;
            border-radius: 50%;
            border: 2px solid #00eaff;
            background: rgba(0,234,255,.06);
            color: #9ff6ff;
            font-size: 27px;
            cursor: pointer;
            box-shadow: 0 0 20px rgba(0,234,255,.25);
            transition: .2s;
        }

        .command-button:hover,
        .command-button.active {
            background: rgba(0,234,255,.18);
            box-shadow:
                0 0 25px rgba(0,234,255,.5),
                inset 0 0 20px rgba(0,234,255,.15);
            transform: scale(1.05);
        }

        .equalizer {
            display: flex;
            align-items: end;
            justify-content: center;
            gap: 4px;
            height: 40px;
            margin-top: 20px;
        }

        .equalizer i {
            display: block;
            width: 4px;
            height: 8px;
            background: #00eaff;
            box-shadow: 0 0 8px #00eaff;
        }

        .equalizer.active i {
            animation: eq .6s ease-in-out infinite alternate;
        }

        .equalizer i:nth-child(2) { animation-delay: .1s; }
        .equalizer i:nth-child(3) { animation-delay: .2s; }
        .equalizer i:nth-child(4) { animation-delay: .3s; }
        .equalizer i:nth-child(5) { animation-delay: .15s; }
        .equalizer i:nth-child(6) { animation-delay: .25s; }
        .equalizer i:nth-child(7) { animation-delay: .05s; }

        @keyframes eq {
            from { height: 6px; }
            to { height: 35px; }
        }

        .log {
            height: 250px;
            overflow-y: auto;
            font-family: monospace;
            font-size: 10px;
            line-height: 1.7;
            color: #65d6e8;
        }

        .log-line {
            border-bottom: 1px solid rgba(0,234,255,.05);
            padding: 3px 0;
        }

        .voice-box {
            margin-top: 15px;
        }

        select {
            width: 100%;
            background: #07131a;
            color: #bff8ff;
            border: 1px solid rgba(0,234,255,.3);
            padding: 10px;
            outline: none;
        }

        .chat {
            margin-top: 15px;
            border: 1px solid rgba(0,234,255,.3);
            background: rgba(3,12,18,.9);
            padding: 12px;
        }

        #messages {
            height: 180px;
            overflow-y: auto;
            padding: 5px;
            margin-bottom: 10px;
        }

        .message {
            margin-bottom: 10px;
            padding: 9px 11px;
            border-left: 2px solid #00eaff;
            background: rgba(0,234,255,.035);
            font-size: 13px;
            line-height: 1.45;
        }

        .message.user {
            border-left-color: #65f6bd;
        }

        .message .who {
            color: #55cfe3;
            font-size: 9px;
            letter-spacing: 2px;
            margin-bottom: 4px;
        }

        .input-row {
            display: flex;
            gap: 8px;
        }

        input {
            flex: 1;
            min-width: 0;
            background: #061017;
            border: 1px solid rgba(0,234,255,.35);
            color: white;
            padding: 13px;
            outline: none;
        }

        input:focus {
            border-color: #00eaff;
            box-shadow: 0 0 10px rgba(0,234,255,.15);
        }

        button.small {
            border: 1px solid #00eaff;
            background: rgba(0,234,255,.06);
            color: #bff8ff;
            padding: 0 16px;
            cursor: pointer;
        }

        button.small:hover {
            background: rgba(0,234,255,.18);
        }

        .mic {
            width: 50px;
            font-size: 19px;
        }

        .terminal {
            margin-top: 15px;
            font-family: monospace;
            font-size: 10px;
            color: #49bccc;
        }

        .terminal-line {
            margin-bottom: 5px;
        }

        .green {
            color: #65f6bd;
        }

        .blue {
            color: #8feeff;
        }

        .warning {
            color: #ffe58a;
        }

        footer {
            text-align: center;
            color: #28636d;
            font-size: 9px;
            letter-spacing: 2px;
            padding: 15px;
        }

        @media (max-width: 950px) {
            .grid {
                grid-template-columns: 1fr;
            }

            .center {
                order: -1;
                min-height: 550px;
            }

            .panel {
                width: 100%;
            }
        }

        @media (max-width: 500px) {
            .app {
                padding: 9px;
            }

            header {
                height: 55px;
            }

            .brand {
                font-size: 17px;
            }

            .center {
                min-height: 470px;
            }

            .core {
                min-width: 220px;
                min-height: 220px;
            }

            .core-letter {
                font-size: 80px;
            }

            .input-row {
                flex-wrap: wrap;
            }

            input {
                width: 100%;
                flex-basis: 100%;
            }

            button.small {
                height: 45px;
            }
        }
    </style>
</head>

<body>

<div id="splash">
    <div class="splash-title">J
