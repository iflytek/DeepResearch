# Copyright (c) 2025 IFLYTEK Ltd.
# SPDX-License-Identifier: Apache 2.0 License

from typing import *
from datetime import datetime

import mistune
from html.parser import HTMLParser

def _check_html(html: str) -> bool:
    try:
        parser = HTMLParser()
        parser.feed(html)
        return True
    except Exception as e:
        return False

class ReportRenderer(mistune.HTMLRenderer):
    def link(self, text: str, url: str, title: Optional[str] = None) -> str:
        if text and text.startswith('^'):
            return f'<span class="citation-ref"><a target="_blank" href="{url}">{text.removeprefix("^")}</a></span>'
        return super().link(text, url, title)

    def block_code(self, code: str, info: Optional[str] = None) -> str:
        if info and info == 'custom_html':
            if _check_html(code):
                return code
            else:
                return ''
        return super().block_code(code, info)

_html_template = '''\
<!DOCTYPE html>
<html>
<head>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <script src="https://gcore.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>
    <script src="https://gcore.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
    
    <link rel="preconnect" href="https://fonts.googleapis.com"/>
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin=""/>
    <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,600;0,700;1,400;1,600&amp;family=Inter:wght@300;400;500;600;700&amp;display=swap" rel="stylesheet"/>
    
    <style>
		:root {
		  --lavender: #A1A9FE;
		  --peach: #F9D7A0;
		  --ink: #161616;
		  --text-primary: #3f3f46;
		  --text-muted: #6b7280;
		  --line-divider: rgba(22, 22, 22, 0.10);
		  --heading-color: #1f2328;
		  --h2-color: #5f5aa5;
		  --highlight: #6b5acc;
		  --page-bg: #ffffff;
		  --glass-bg: rgba(255, 255, 255, 0.8);
		  --glass-border: rgba(255, 255, 255, 0.78);
		  --chip-bg: rgba(255, 255, 255, 0.65);
		  --s1: 6px; --s2: 10px; --s3: 14px; --s4: 18px;
		  --s5: 24px; --s6: 32px; --s7: 48px;
		  --measure: 97ch;
		
		  --lh-solid: 1.1;
		  --lh-tight: 1.35;
		  --lh-snug:  1.5;
		  --lh-normal: 1.7;
		  --lh-relaxed: 1.85;
		}
		
		.brutalist-theme {
		  --black: #111111;
		  --white: #ffffff;
		  --off-white: #f5f5f5;
		  --accent: #cafa69;
		  --number: #fdccff;
		  --background:#1f1f1f;
		  --highlight:#fffeec;
		  --bold: #7c6ef5;
		}
		
		* { box-sizing: border-box; }
		html { font-size: 16px; }
		
		body {
		  margin: 0;
		  color: var(--text-primary);
		  font-family: "Source Han Sans SC", "Noto Sans SC", "Noto Sans CJK SC", "PingFang SC", "Morise UD Sans", "Montserrat", sans-serif, "Hiragono Sans GB", "Microsoft YaHei", ui-sans-serif, system-ui, -apple-system, "Segoe UI", Roboto, Arial, sans-serif;
		  -webkit-font-smoothing: antialiased;
		  text-rendering: optimizeLegibility;
		  background-attachment: fixed;
		  background:
			radial-gradient(1500px 880px at 50% 50%, rgba(106, 90, 205, 0.14), transparent 62%),
			radial-gradient(1800px 900px at 12% 8%, rgba(161, 169, 254, 0.22), transparent 60%),
			radial-gradient(1600px 820px at 85% 20%, rgba(249, 215, 160, 0.22), transparent 60%),
			radial-gradient(1450px 800px at 40% 95%, rgba(173, 143, 255, 0.12), transparent 60%),
			linear-gradient(180deg, #fafafe 0%, #ffffff 85%, #ffffff 100%);
		  transition: background 0.2s ease;
		  position: relative; 
		  z-index: 1;
		  line-break: loose;                
		  font-kerning: normal;
		  font-feature-settings: "palt" 1; 
		}
		
		body::before {
		  content: "";
		  position: fixed;
		  top: 0; left: 0; right: 0; bottom: 0;
		  box-shadow: inset 0 0 15vw 10vw rgba(161, 169, 254, 0.08);
		  pointer-events: none; 
		  z-index: -1;
		}

		.brutalist-theme {
		  background: var(--background);
		  background-attachment: scroll;
		  color: var(--off-white);
		}
		body.brutalist-theme::before {
			display: none;
		}
		
		.container {
		  max-width: var(--measure);
		  margin: 0 auto;
		  padding: var(--s7) var(--s6);
		  position: relative;
		  isolation: isolate; 
		}
		
		.container::before {
		  content: "";
		  position: absolute;
		  inset: clamp(20px, 3vw, 40px);
		  z-index: 0;               
		  border-radius: 28px;
		  pointer-events: none;
		  background:
			radial-gradient(1200px 700px at 20% 10%, rgba(255,255,255,.22), transparent 60%),
			radial-gradient(1000px 600px at 85% 20%, rgba(255,255,255,.18), transparent 60%),
			linear-gradient(180deg, rgba(255,255,255,.38), rgba(255,255,255,.18));
		  backdrop-filter: blur(18px) saturate(150%);
		  -webkit-backdrop-filter: blur(18px) saturate(150%);
		  box-shadow:
			0 30px 80px -40px rgba(61,70,125,.22),
			inset 0 1px 1.2px rgba(255,255,255,.65);
		}
		
		.brutalist-theme .container::before {
		  content: none;
		}
		
		.content-card {
		  position: relative;
		  z-index: 1;
		  background: rgba(255, 255, 255, 0.92);
		  border: 1px solid rgba(255,255,255,0.55);
		  border-radius: 18px;
		  padding: 3rem 4rem;
		  backdrop-filter: blur(6px) saturate(130%); 
		  -webkit-backdrop-filter: blur(6px) saturate(130%);
		  box-shadow:
			0 16px 40px -12px rgba(120,120,160,.20),
			inset 0 0 0 0.8px rgba(255,255,255,.85);
		  line-height: var(--lh-relaxed); 
		  counter-reset: sec;
		}
		.content-card::before {
		  display: none;
		}
		.brutalist-theme .content-card {
		  background: var(--background); 
		  border: none;
		  border-radius: 0;
		  box-shadow: none;
		  backdrop-filter: none;
		}
		.brutalist-theme .content-card::before {
		  display: none;
		}
		.company-logo {
		  display: flex; align-items: center; gap: 10px;
		  font-weight: 800; font-size: 18px; letter-spacing: -0.01em;
		  color: var(--ink);
		  margin-bottom: var(--s5);
		}
		.company-logo::before {
		  content: "";
		  width: 22px; height: 22px; border-radius: 8px;
		  background: linear-gradient(135deg, var(--lavender), var(--peach));
		  box-shadow: 0 6px 12px rgba(161, 169, 254, 0.30);
		}
		.brutalist-theme .company-logo {
		  color: var(--white);
		}
		.brutalist-theme .company-logo::before {
		  border-radius: 0;
		  background: var(--white);
		  box-shadow: none;
		}
		
		h1, .report-title, h2, h3 {
		  color: var(--heading-color);
		  position: relative;
		  z-index: 1;
		}
		.brutalist-theme h1, .brutalist-theme h2, .brutalist-theme h3 {
			color: var(--white);
		}
		h1, .report-title {
		  font-size: 2.2rem;
		  line-height: var(--lh-tight);
		  font-weight: 800; letter-spacing: -0.02em;
		  margin: 1rem 0 2rem;
		}
		h2 {
		  counter-increment: sec;
		  font-size: 1.6rem;
		  line-height: var(--lh-tight); 
		  font-weight: 750; letter-spacing: -0.015em;
		  margin: 3.5rem 0 1.8rem;
		  padding-bottom: .2rem;
		  color: var(--h2-color);
		  text-wrap: balance; 
		}
		h2::before {
		  content: counter(sec, decimal-leading-zero);
		  position: absolute; left: -6px; top: 50%;
		  transform: translateY(-55%);
		  font-size: clamp(48px, 7vw, 84px);
		  font-weight: 900; letter-spacing: -0.02em; line-height: 0.9;
		  color: rgba(0, 0, 0, 0.045);
		  pointer-events: none; z-index: 0;
		}
		.brutalist-theme h2 {
		  color: var(--number);
		  font-weight: 500;
		  padding-left: 40px;
		  counter-increment: none;
		}
		.brutalist-theme h2::before {
		  content: "“";
		  font-family: 'Georgia', Times, serif;
		  color: var(--number);
		  font-size: clamp(65px, 9vw, 85px);
		  font-weight: 400;
		  left: -10px; top: -18px;
		  line-height: 1;
		  transform: none;
		}
		h3 {
		  font-size: 1.25rem;
		  font-weight: 700; letter-spacing: -0.01em;
		  line-height: var(--lh-snug);
		  margin: 2.5rem 0 1.2rem;
		  padding-bottom: .3rem;
		}
		.report-meta {
		  display: flex; flex-wrap: wrap; gap: 10px 16px;
		  color: var(--text-muted); font-size: 13px;
		  margin-bottom: var(--s3);
		}
		.report-meta div { display: inline-flex; align-items: center; gap: 6px; }
		.report-meta div::before { content: "•"; color: #bdbdbd; }
		.brutalist-theme .report-meta { color: var(--off-white); }
		p {
		  font-size: 16px;
		  text-align: left;
		  margin: 0 0 1.5rem;
		  text-wrap: pretty;
		}
		strong { 
			color: var(--heading-color); 
			margin: 0 0.13em;
			font-weight: 600;
		}
		.brutalist-theme strong { color: var(--accent);}
		a {
		  color: inherit; text-decoration: none;
		  background-image: linear-gradient(120deg, var(--lavender), var(--peach));
		  background-size: 0 2px; background-position: 0 100%;
		  background-repeat: no-repeat;
		  transition: background-size 0.2s ease;
		}
		a:hover { background-size: 100% 2px; }
		.brutalist-theme a {
		  background-image: none;
		  transition: background-color 0.2s ease, color 0.2s ease;
		}
		.brutalist-theme a:hover {
		  background-color: var(--accent);
		  color: var(--black);
		}

		img {
		  display: block; margin: 1.6rem auto 1.8rem;
		  max-width: 100%; height: auto;
		  border-radius: 14px;
		  border: 1px solid rgba(255, 255, 255, 0.7);
		  background: rgba(255, 255, 255, 0.6);
		  box-shadow: 0 20px 40px rgba(61, 70, 125, 0.12), 0 1px 0 rgba(255, 255, 255, 0.6) inset;
		}
		.brutalist-theme img {
		  border-radius: 0;
		  border: 2px solid var(--white);
		  background: var(--white);
		  box-shadow: none;
		}
		blockquote {
		  margin: 2.5rem 0; 
		  padding: var(--s4) var(--s5);
		  background: rgba(255, 255, 255, 0.65);
		  border: 1px solid var(--glass-border);
		  border-radius: 12px;
		  backdrop-filter: blur(6px);
		  position: relative;
		}
		blockquote::before {
		  content: "";
		  position: absolute; left: 0; top: 0; bottom: 0;
		  width: 3px; border-radius: 12px 0 0 12px;
		  background: #f48d45;
		}
		.brutalist-theme blockquote {
		  background: var(--black);
		  border: 2px solid var(--accent);
		  border-radius: 0;
		  backdrop-filter: none;
		}
		.brutalist-theme blockquote::before {
		  display: none;
		}
		
		ul {
		  font-size: 15px;
		  font-weight: 450;
		  line-height: 1.9;
		  font-family: "Morise UD Sans", "Montserrat", sans-serif;
		  margin: 2.2rem 0;
		  list-style-type: none;
		  padding: 1.2rem;
		  background-color: rgba(238, 240, 251, 0.682);
		  border-radius: 12px;
		}
		ol {
		  margin: 1rem 0; 
		  padding-left: 1.5rem;
		  list-style-position: outside;
		}
		ul li {
		  position: relative;
		  padding-left: 1.5em;
		}
		ol li {
		  padding-left: 0.5em;
		  text-indent: 0;
		}
		li:not(:last-child) {
		  margin-bottom: 0.8rem; 
		}
		ol li:not(:last-child) {
		  margin-bottom: 0.4rem;
		}
		ul li::before {
		  content: '✦';
		  position: absolute;
		  left: 0; 
		  color: var(--h2-color);
		}
		.brutalist-theme ul {
			background: #3a3a3a;
			border: none;
			border-radius: 12px;
		}
		.brutalist-theme ul li::before {
			content: '❋';
			color: var(--number);
			margin-right: 0.5em;
		}
		
		table {
		  width: 100%;
		  border-spacing: 0;
		  margin: 2.2rem 0; 
		  background: rgba(255, 255, 255, 0.70);
		  border: none;
		  border-radius: 14px;
		  overflow: hidden;
		  backdrop-filter: blur(6px);
		  border-collapse: separate;
		  table-layout: auto;
		}
		th, td {
		  padding: 10px 6px;
		  border-bottom: 1px solid var(--line-divider);
		  font-size: 14px;
		  text-align: center;
		  overflow-wrap: break-word;
		}
		th {
		  background: var(--highlight); color: #fff;
		  font-weight: 700;
		  font-size: 14px;
		}
		thead th:first-child { border-top-left-radius: 13px; }
		thead th:last-child { border-top-right-radius: 13px; }
		tbody tr:nth-child(even) { background: rgba(255, 255, 255, 0.65); }
		tbody tr:hover { background: color-mix(in oklab, var(--lavender) 12%, white); }
		
		.brutalist-theme table {
		  border-collapse: collapse;
		  background: none;
		  border: 1px solid var(--white);
		  border-radius: 0;
		  backdrop-filter: none;
		  table-layout: auto;
		}
		.brutalist-theme th, .brutalist-theme td {
		  border: 1px solid var(--white);
		  overflow-wrap: break-word;
		}
		.brutalist-theme th {
		  background: var(--bold);
		  color: var(--white);
		}
		.brutalist-theme thead th:first-child,
		.brutalist-theme thead th:last-child {
		  border-radius: 0;
		}
		.brutalist-theme tbody tr:nth-child(even) { background: transparent; }
		.brutalist-theme tbody tr:hover { background: var(--highlight); color: var(--black); }
		
		tbody tr:hover .citation-ref a {
		  background-color: var(--h2-color);
		  color: white;
		  box-shadow: none; 
		}
		.brutalist-theme tbody tr:hover .citation-ref a {
		  background-color: var(--accent);
		  color: var(--black);
		}
		.brutalist-theme tbody tr:hover strong {
		  color: var(--black);
		}
		
		caption {
		  caption-side: top;
		  text-align: center;
		  font-size: 16px;
		  font-weight: 700;
		  color: var(--h2-color);
		  padding-bottom: 1rem;
		}
		.brutalist-theme caption {
		  color: #9b9bff;
		}
		
		.citation-ref {
		  white-space: nowrap;
		}
		.citation-ref::before {
		  content: ' ';
		}
		.citation-ref + .citation-ref::before {
		  content: '';
		}
		.citation-ref a {
		  display: inline-flex;
		  justify-content: center;
		  align-items: center; 
		  line-height: 1; text-align: center;
		  width: 1.5em;  height: 1.5em;
		  padding: 0; border-radius: 50%;
		  font-variant-numeric: tabular-nums;
		  font-feature-settings: "palt" 0;
		  vertical-align: super;
		  font-size: 0.6em;
		  font-weight: 500;
		  color: white; 
		  margin: 0 1px;
		  padding: 0px; 
		  background-color: #b2b3d9; 
		  transition: all 0.2s ease;
		}
		.citation-ref a:hover {
		  background-color: var(--h2-color);
		  color: white;
		  border-color: transparent;
		}
		.brutalist-theme .citation-ref a {
		  color: var(--accent);
		  background-color: rgba(255, 255, 255, 0.1);
		  font-weight: 500;
		  box-shadow: none;
		  border: none;
		}
		.brutalist-theme .citation-ref a:hover {
		  background-color: var(--accent);
		  color: var(--black);
		}
		
		hr {
		  border: none; height: 1px;
		  background: linear-gradient(90deg, rgba(161, 169, 254, 0.4), rgba(249, 215, 160, 0.4));
		  margin: var(--s6) 0;
		}
		.brutalist-theme hr {
		  height: 2px;
		  background: var(--white);
		}
		
		.chart-title {
		  text-align: center;
		  font-size: 15px;
		  font-weight: 700;
		  color: var(--h2-color);
		  padding-bottom: 1rem;
		}
		.brutalist-theme .chart-title {
		  color: #9b9bff;
		}
		.chart-container {
		  width: 100%; max-width: 100%;
		  aspect-ratio: 5 / 3; 
		  margin: 2rem 0 0.5rem;
		}
		.chart-data-source, .table-data-source {
		  font-size: 13px; color: var(--text-muted);
		  text-align: left;
		  margin-top: 0; 
		  margin-bottom: 2rem;
		}
		.brutalist-theme .chart-data-source, .brutalist-theme .table-data-source {
		  color: var(--off-white);
		}
		@media (max-width: 768px) {
		  html { font-size: 15px; }
		  .container { padding: var(--s6) var(--s4); }
		  .content-card { padding: var(--s5) var(--s5); border-radius: 16px; }
		  h2::before { left: -2px; font-size: 64px; }
		  .brutalist-theme h2::before { left: -2px; font-size: 64px; }
		}
		
		.style-switcher {
			position: fixed;
			top: 15px;
			right: 20px;
			z-index: 9999;
			background: rgba(255, 255, 255, 0.8);
			backdrop-filter: blur(8px);
			border-radius: 8px;
			padding: 6px;
			box-shadow: 0 4px 12px rgba(0,0,0,0.1);
			display: flex;
			align-items: center;
			gap: 8px;
			border: 1px solid rgba(0,0,0,0.05);
		}
		.style-switcher span {
			font-size: 13px;
			color: #333;
			margin-left: 4px;
		}
		.style-switcher button {
			border: none;
			padding: 6px 12px;
			font-size: 13px;
			border-radius: 6px;
			cursor: pointer;
			background-color: transparent;
			color: #555;
			font-weight: 500;
			transition: all 0.2s ease;
		}
		.style-switcher button.active {
			background-color: var(--highlight);
			color: white;
			box-shadow: 0 2px 4px rgba(0,0,0,0.1);
		}
		.brutalist-theme .style-switcher {
			background: var(--white);
			border: 2px solid var(--black);
			box-shadow: 4px 4px 0 var(--white);
			backdrop-filter: none;
		}
		.brutalist-theme .style-switcher button.active {
			background-color: var(--black);
		}

        .citation-popup {
            position: absolute;
            background-color: white;
            border-radius: 8px;
            width: 340px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
            padding: 1rem;
            z-index: 9999;
            opacity: 0;
            visibility: hidden;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            transform: translateY(8px);
            pointer-events: none;
        }

        .citation-popup.active {
            opacity: 1;
            visibility: visible;
            transform: translateY(0);
            pointer-events: auto;
        }

        .citation-popup::after {
            content: '';
            position: absolute;
            width: 10px;
            height: 10px;
            background-color: white;
            transform: rotate(45deg);
            box-shadow: 3px -3px 5px rgba(0, 0, 0, 0.03);
        }

        .popup-header {
            font-size: 0.95rem;
            font-weight: 600;
            color: #333;
            margin-bottom: 0.75rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }

        .popup-header svg {
            width: 1rem;
            height: 1rem;
            color: #5F5AA5;
        }

		.popup-excerpt {
			font-size: 12px;
			color: #666;
			padding: 0.75rem;
			background-color: #f8fafc;
			border-radius: 6px;
			margin-bottom: 0.75rem;
			line-height: 1.5;
			border-left: 2px solid #5F5AA5;
			overflow: hidden;
			text-overflow: ellipsis;
			display: -webkit-box;
			-webkit-line-clamp: 5;
			-webkit-box-orient: vertical;
			word-break: break-word;
			white-space: normal;
			max-height: calc(1.7em * 5);
		}

        .popup-actions {
            display: flex;
            justify-content: flex-end;
        }

        .visit-btn {
            padding: 0.4rem 0.9rem;
            border-radius: 6px;
            border: none;
            cursor: pointer;
            transition: all 0.2s ease;
            font-weight: 500;
            background-color: #5F5AA5;
            color: white;
            font-size: 0.85rem;
        }

        .visit-btn:hover {
            background-color: #4a468a;
            transform: translateY(-1px);
        }

        @media (max-width: 640px) {
            .citation-popup {
                width: calc(100vw - 3rem);
                max-width: 300px;
            }
        }
	</style>
</head>
<body>
<div class="style-switcher">
	<button id="modern-btn" class="active">Light</button>
	<button id="brutalist-btn">Dark</button>
</div>
<div class="container">
  <div class="content-card">
    {content}
  </div>
</div>

<div class="citation-popup" id="citationPopup">
	<div class="popup-header">
		<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
			<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path>
		</svg>
	</div>
	<div class="popup-excerpt" id="popupExcerpt"></div>
</div>

<script>
    (function () {
        'use strict';

        const modernBtn = document.getElementById('modern-btn');
        const brutalistBtn = document.getElementById('brutalist-btn');
        const body = document.body;

        const paletteLight = [
            '#3d2f6e', '#6b5acc', '#8A75D6', '#a49de3',
            '#A2BBDC', '#BCCDE4', '#DCE4F0', '#FEF8E5',
            '#FDF2D0', '#FBE6A4'
        ];
        const paletteDark = [
            '#7c6ef5', '#fffeec', '#fdccff'
        ];

        function getThemeUI() {
            const isDark = document.body.classList.contains('brutalist-theme');
            if (isDark) {
                return {
                    isDark: true,
                    text: '#E8EAED',
                    axis: '#9AA0A6',
                    grid: '#2F3B45',
                    palette: paletteDark,
                    tooltip: {
                        backgroundColor: 'rgba(50, 50, 50, 0.7)',
                        borderColor: '#E8EAED',
                        textStyle: { color: '#E8EAED' }
                    }
                };
            }
            return {
                isDark: false,
                text: '#20396D',
                axis: '#9CA3AF',
                grid: '#E5E7EB',
                palette: paletteLight,
                tooltip: {
                    backgroundColor: 'rgba(255, 255, 255, 0.7)',
                    borderColor: '#333',
                    textStyle: { color: '#333' }
                }
            };
        }

        function buildAxisStyle(ui) {
            return {
                axisLabel: { color: ui.text },
                axisLine: { show: false, lineStyle: { color: ui.axis } },
                splitLine: { show: false, lineStyle: { color: ui.grid } }
            };
        }

        function updateChartTheme(isBrutalist) {
            const chartContainers = document.querySelectorAll('.chart-container');
            chartContainers.forEach(container => {
                const myChart = echarts.getInstanceByDom(container);
                if (myChart) {
                    const ui = getThemeUI();
                    const axisStyle = buildAxisStyle(ui);

                    myChart.setOption({
                        backgroundColor: 'transparent',
                        color: ui.palette,
                        textStyle: { color: ui.text },
                        legend: { textStyle: { color: ui.text } },
                        title: { textStyle: { color: ui.text } },
                        xAxis: axisStyle,
                        yAxis: axisStyle,
                        tooltip: {
                            ...ui.tooltip,
                            borderWidth: 1
                        },
						polar: {
							axisLine: { show: false,lineStyle: { color: ui.axis } }
						},
						angleAxis: {
							axisLine: { show: false,lineStyle: { color: ui.axis } }
						},
						radiusAxis: {
							axisLine: { show: false,lineStyle: { color: ui.axis } }
						},
						series: {
							label: {color: ui.text},
							labelLine: {lineStyle: {color: ui.text}},
							emphasis: {label: {color: ui.text}}
						}
                    }, false, false);
                }
            });
        };

        modernBtn.addEventListener('click', () => {
            body.classList.remove('brutalist-theme');
            modernBtn.classList.add('active');
            brutalistBtn.classList.remove('active');
            updateChartTheme(false);
        });

        brutalistBtn.addEventListener('click', () => {
            body.classList.add('brutalist-theme');
            brutalistBtn.classList.add('active');
            modernBtn.classList.remove('active');
            updateChartTheme(true);
        });

        function debounce(func, wait) {
            let timeout;
            return function (...args) {
                clearTimeout(timeout);
                timeout = setTimeout(() => func.apply(this, args), wait);
            };
        }

        function loadScript(src, { timeout = 15000 } = {}) {
            return new Promise((resolve, reject) => {
                const s = document.createElement('script');
                let done = false;
                const timer = setTimeout(() => {
                    if (done) return;
                    done = true;
                    s.remove();
                    reject(new Error(`Load timeout: ${src}`));
                }, timeout);
                s.src = src;
                s.async = true;
                s.onload = () => {
                    if (done) return;
                    done = true;
                    clearTimeout(timer);
                    resolve();
                };
                s.onerror = () => {
                    if (done) return;
                    done = true;
                    clearTimeout(timer);
                    reject(new Error(`Failed to load: ${src}`));
                };
                document.head.appendChild(s);
            });
        }

        async function ensureEchartsLoaded() {
            if (typeof window.echarts !== 'undefined') return;
            const cdns = [    
				'https://https://gcore.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js',
                'https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js',
                'https://unpkg.com/echarts@5.4.3/dist/echarts.min.js'
            ];
            let lastErr;
            for (const url of cdns) {
                try {
                    await loadScript(url);
                    if (typeof window.echarts !== 'undefined') return;
                } catch (e) {
                    lastErr = e;
                }
            }
            throw lastErr || new Error('ECharts CDN load failed');
        }

        const DomProcessor = {
            init(scopeSelector) {
                const contentScope = document.querySelector(scopeSelector) || document.body;
                if (!contentScope) return;

                this.removeChapterNumerals(contentScope);
                this.transformMarkdownBold(contentScope);
                this.addInterScriptSpacing(contentScope);
            },

            removeChapterNumerals(scope) {
                const chapterNumeralRegex = /^[一二三四五六七八九十百千]+[、\.．]\s*/;
                scope.querySelectorAll('h2').forEach(h => {
                    h.textContent = h.textContent.replace(chapterNumeralRegex, '').trim();
                });
            },

            transformMarkdownBold(scope) {
                const textElementsSelector = 'p, li, td, th, blockquote';
                const elements = scope.querySelectorAll(textElementsSelector);
                const boldRegex = /\*\*([^*]+?)\*\*/g;

                elements.forEach(el => {
                    const walker = document.createTreeWalker(el, NodeFilter.SHOW_TEXT);
                    const nodesToProcess = [];
                    let node;
                    while ((node = walker.nextNode())) {
                        if (
                            node.parentNode.tagName !== 'CODE' &&
                            node.parentNode.tagName !== 'A' &&
                            boldRegex.test(node.nodeValue)
                        ) {
                            nodesToProcess.push(node);
                        }
                    }
                    nodesToProcess.forEach(textNode => {
                        const fragment = document.createDocumentFragment();
                        let lastIndex = 0;
                        textNode.nodeValue.replace(boldRegex, (match, p1, offset) => {
                            fragment.appendChild(
                                document.createTextNode(textNode.nodeValue.slice(lastIndex, offset))
                            );
                            const strong = document.createElement('strong');
                            strong.textContent = p1;
                            fragment.appendChild(strong);
                            lastIndex = offset + match.length;
                        });
                        fragment.appendChild(
                            document.createTextNode(textNode.nodeValue.slice(lastIndex))
                        );
                        textNode.parentNode.replaceChild(fragment, textNode);
                    });
                });
            },

            addInterScriptSpacing(scope) {
                const THIN_SPACE = ' ';
                const cjkLatinRegex = /([一-龥＀-￯])([a-zA-Z0-9])/g;
                const latinCjkRegex = /([a-zA-Z0-9])([一-龥＀-￯])/g;

                const walker = document.createTreeWalker(scope, NodeFilter.SHOW_TEXT);
                let node;
                while ((node = walker.nextNode())) {
                    if (['STYLE', 'SCRIPT', 'PRE', 'CODE', 'A', 'STRONG'].includes(node.parentNode.tagName)) {
                        continue;
                    }
                    node.nodeValue = node.nodeValue
                        .replace(cjkLatinRegex, `$1${THIN_SPACE}$2`)
                        .replace(latinCjkRegex, `$1${THIN_SPACE}$2`);

                    const nextSibling = node.nextSibling;
                    if (nextSibling && nextSibling.nodeType === Node.ELEMENT_NODE && nextSibling.tagName === 'STRONG') {
                        continue;
                    }
                    const currentText = node.nodeValue;
                    if (!currentText) continue;
                    const nextText = nextSibling ? nextSibling.textContent : '';
                    if (!nextText) continue;
                    const lastChar = currentText.slice(-1);
                    const firstChar = nextText.slice(0, 1);
                    const isCjk = ch => /[一-龥＀-￯]/.test(ch);
                    const isLatin = ch => /[a-zA-Z0-9]/.test(ch);
                    if (!currentText.endsWith(THIN_SPACE) && !currentText.endsWith(' ')) {
                        if ((isCjk(lastChar) && isLatin(firstChar)) || (isLatin(lastChar) && isCjk(firstChar))) {
                            node.nodeValue += THIN_SPACE;
                        }
                    }
                }
            }
        };

        const ChartManager = {
            instances: [],

            async init() {
                try {
                    await ensureEchartsLoaded();
                } catch (e) {
                    console.error('can not load ECharts：', e);
                    return;
                }
                this.hookEchartsInit();
                this.setupResizeListener();
                updateChartTheme();
            },

            hookEchartsInit() {
                const originalInit = echarts.init;
                const self = this;

                let existingInstances = [];
                const chartContainers = document.querySelectorAll('.chart-container');
                chartContainers.forEach(dom => {
                    const instance = echarts.getInstanceByDom(dom);

                    if (instance) {
                        existingInstances.push(instance);
                    }
                });
                self.instances.push(...existingInstances);
            },

            setupResizeListener() {
                const debouncedResize = debounce(() => {
                    this.instances.forEach(inst => {
                        if (inst && !inst.isDisposed()) inst.resize();
                    });
                }, 200);
                window.addEventListener('resize', debouncedResize);
            },
        };

        document.addEventListener('DOMContentLoaded', async () => {
            DomProcessor.init('.content-card');
            await ChartManager.init();
        });
    })();

</script>
<script>
    document.addEventListener('DOMContentLoaded', function () {
        const modernBtn = document.getElementById('modern-btn');
        const brutalistBtn = document.getElementById('brutalist-btn');
        const body = document.body;

        const setTheme = (theme) => {
            if (theme === 'brutalist') {
                body.classList.add('brutalist-theme');
                modernBtn.classList.remove('active');
                brutalistBtn.classList.add('active');
                localStorage.setItem('reportTheme', 'brutalist');
            } else {
                body.classList.remove('brutalist-theme');
                modernBtn.classList.add('active');
                brutalistBtn.classList.remove('active');
                localStorage.setItem('reportTheme', 'modern');
            }
        };

        modernBtn.addEventListener('click', () => setTheme('modern'));
        brutalistBtn.addEventListener('click', () => setTheme('brutalist'));

        setTheme('modern');
    });
</script>
</body>
</html>
'''

def markdown2html(title:str, markdown:str) -> str:
    """
    Convert markdown to html.
    """
    gsm = ['url', 'table', 'strikethrough', 'task_lists']
    convert = mistune.create_markdown(escape=False, renderer=ReportRenderer(), plugins=gsm)
    content = convert(markdown)
    html = _html_template.replace('{title}', title).replace('{content}', content)
    return html

_test_md = '''
# 写字楼园区高盈利餐饮业态投资策略分析

## 一、市场概况分析
### 1.1 写字楼餐饮市场迎来场景化升级，租金成本优势驱动创业热潮

全国主要城市核心商务区平均每栋写字楼聚集**2000-5000名白领**，其中**86%的上班族存在工作日午餐刚需**，形成高密度、稳定且可预估的消费场景[^3]。这一特征驱动写字楼餐饮创业热潮，其租金占比通常可控制在**15%-20%的安全线内**，显著低于核心商圈，且可通过强调服务租户价值争取更弹性租金条件与免租期[^4]。进一步看，写字楼餐饮门店普遍呈现"三低一高"特征：场地面积需求低（50-150㎡）、装修投入低（标准化动线设计）、人力配置低（中央厨房支撑），而坪效产出高，对比同等面积的社区餐饮店通常能实现**2-3倍的翻台率**[^3]。客流高度集中于工作日午间，具备精准的"时段经济"特征，支持食材备货可控、员工排班高效、厨房产能集中爆发，午市两小时可实现全天**70%的营收**[^4]。以某二线城市CBD的中型写字楼为例，若覆盖3000名白领，按人均30元客单价、50%转化率计算，单日午餐营业额可达**4.5万元**，叠加早餐、下午茶等场景延伸，实际盈利能力更具想象空间[^3]。

### 1.2 健康轻食与智能服务主导行业新趋势，复合业态盈利表现突出

我国轻食市场规模已超过**500亿元**，预计到2025年将突破**1000亿元**，消费者对轻食的需求主要集中在沙拉、轻食套餐、轻食外卖等方面，契合写字楼白领群体对便捷、健康餐饮的高频需求[^5^]。轻食行业满足人们对便捷、健康、低卡、高营养的饮食需求，消费群体主要集中在白领人群、健身爱好者及注重饮食健康的人群[^6]。产品趋向多样化与个性化，从传统三明治、沙拉扩展至低卡餐、素食餐，并提供根据体重、运动量和营养需求定制的专属套餐[^6]。复合型连锁餐厅通过融合轻食简餐、下午茶社交、夜间小酒馆三重业态，构建全天候盈利模型，单店日均客流量可达**120-150人次**，较传统模式提升**45%以上**[^8]。以北京某写字楼轻食店为例，通过"咖啡简餐+共享会议室"的业态组合，日均客流量达**380人次**，超过**42%**的顾客在购买餐食后使用会议空间，带动客单价从28元提升至**89元**，坪效达到传统餐饮店的**2.3倍**[^7]。

智能点餐系统通过AI算法提升餐厅运营效率，前端扫码点餐使服务响应速度提升**50%以上**，后厨订单管理系统提高出餐效率**30%**，平均翻台率提升**20%-30%**[^2]。应用智能推荐系统的餐厅，顾客人均消费额平均提升**15%**，例如主营中式快餐的案例门店通过推送"热销套餐+当季新品"组合，套餐转化率达到**42%**，较传统纸质菜单提升近三倍[^2]。智能点餐系统的初期投入仅需**3-5万元**（含硬件设备及系统授权），相比传统POS系统降低**60%成本**[^2]。某创业者在二线城市加盟智能点餐系统后，单店月均订单量突破**6500单**，顾客复购率达到**38%**，并通过消费数据分析将食材损耗率从12%降低至7%，每月节省成本近万元[^2]。预计到2030年，中国餐饮业人工智能点餐系统的渗透率将提升至**70%以上**，其中大型连锁餐饮企业采用比例将达**80%**，小型及中型企业也将超过**60%**[^1]。

``` custom_html
<div id="1760497713843" class="chart-container" style="width:800px; height:600px; "></div>
    <script>
    var chartDom = document.getElementById('1760497713843');
    var myChart = echarts.init(chartDom);
    var option;

    chartDom.style.display = 'block';

    var chartData = {
  title: "轻食市场规模增长趋势",
  xAxisData: [
    "当前",
    "2025"
  ],
  seriesData: [
    {
      name: "市场规模",
      type: "bar",
      data: [
        500,
        1000
      ]
    }
  ],
  yAxisName: [
    "亿元"
  ],
  toolbox: {
    show: true,
    feature: {
      dataView: {
        title: "数据说明",
        lang: [
          "",
          "返回",
          ""
        ],
        optionToContent: function (opt) {
          return "<p><strong>从文本中提取了轻食市场的当前规模500亿元和2025年预计达到的1000亿元数据，使用柱状图展示市场规模的增长趋势。</strong></p>";
        },
        icon: "path://M432.45,595.444c0,2.177-4.661,6.82-11.305,6.82c-6.475,0-11.306-4.567-11.306-6.82s4.852-6.812,11.306-6.812C427.841,588.632,432.452,593.191,432.45,595.444L432.45,595.444z M421.155,589.876c-3.009,0-5.448,2.495-5.448,5.572s2.439,5.572,5.448,5.572c3.01,0,5.449-2.495,5.449-5.572C426.604,592.371,424.165,589.876,421.155,589.876L421.155,589.876z M421.146,591.891c-1.916,0-3.47,1.589-3.47,3.549c0,1.959,1.554,3.548,3.47,3.548s3.469-1.589,3.469-3.548C424.614,593.479,423.062,591.891,421.146,591.891L421.146,591.891zM421.146,591.891",
        readOnly: true
      }
    }
  }
};

var seriesData = [];
for (let i = 0; i < chartData.seriesData.length; i++) {
   let obj = chartData.seriesData[i];
   if (obj.type == 'bar') {
      seriesData.push({
         name: obj.name,
         type: 'bar',
         barWidth: chartData.barWidth || 20,
         itemStyle: {
            borderWidth: 2
         },
         data: obj.data
      });
   } else if (obj.type == 'line') {
      let o = {
         name: obj.name,
         type: 'line',
         symbol: 'circle',
         symbolSize: 10,
         itemStyle: {
            borderWidth: 2,
         },
         lineStyle: {
            width: 2,
         },
         yAxisIndex: 1,
         data: obj.data
      };
      seriesData.push(o);
   }
}
option = {
   ...(chartData.toolbox ? { toolbox: chartData.toolbox } : {}),
   title: {
    text: chartData.title,
    x: "center",
    y: "up",
	 textStyle: {
         padding: [0, 0, 0, 5]
      }
  },
   grid: {
      left: 100,
      bottom: 100,
      right: 100,
      top: 140,
      containLabel: true,
   },
   legend: {
      width: '100%',
      right: 'center',
      bottom: 50,
      textStyle: {
         padding: [0, 0, 0, 5]
      },
      itemStyle: {
         borderWidth: 0,
      },
      itemWidth: 24,
      itemHeight: 12,
      itemGap: 35
   },
   tooltip: {
      trigger: 'axis',
      axisPointer: {
         type: 'shadow'
      }
   },
   xAxis: {
      type: 'category',
      axisTick: {
         show: false,
      },
      axisLine: {
         symbol: ['none', 'arrow'],
         symbolSize: [10, 10],
         symbolOffset: [0, 10],
         lineStyle: {
            color: '#0B5EA0',
         }
      },
      axisLabel: {
         margin: 20,
      },
	  data: chartData.xAxisData
   },
   yAxis: [{
      type: 'value',
      name: (chartData.yAxisName && chartData.yAxisName[0]) || '',
      nameGap: 20,
      axisTick: {
         show: false,
      },
      axisLine: {
         show: true,
         lineStyle: {
            color: '#0C5B9B',
         }
      },
      splitLine: {
         show: true,
         lineStyle: {
            color: '#11456F'
         }
      },
      splitArea: {
         show: true,
      },
      axisLabel: {
         margin: 20
      }
   }, {
      type: 'value',
      name: (chartData.yAxisName && chartData.yAxisName[1]) || '',
      nameGap: 20,
      axisTick: {
         show: false,
      },
      splitLine: {
         show: false,
      },
      axisLine: {
         show: false,
      },
      axisLabel: {
         margin: 20
      }
   }],
   series: seriesData
};;

    myChart.setOption(option);
    </script>
```

数据来源:[^3]

[^1]: https://www.renrendoc.com/paper/476932463.html
[^2]: https://jiameng.baidu.com/content/detail?id=309187959842
[^3]: https://jiameng.baidu.com/content/detail?id=737970097894
[^4]: https://baijiahao.baidu.com/s?id=1837363162619235727
[^5]: https://m.renrendoc.com/paper/423690601.html
'''

if __name__ == '__main__':
    html = markdown2html('Test', _test_md)
    with open('test.html', 'wb') as f:
        f.write(html.encode('utf-8'))
