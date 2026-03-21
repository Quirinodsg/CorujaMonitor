import React, { useState, useEffect } from "react";
import "./Sidebar.css";

var CATS = [
  { id: "monitoring", label: "Monitoramento", icon: "📊", items: [
    { id: "dashboard",  icon: "📊", label: "Dashboard" },
    { id: "companies",  icon: "🏢", label: "Empresas" },
    { id: "servers",    icon: "🖥️", label: "Servidores" },
    { id: "sensors",    icon: "📡", label: "Sensores" },
  ]},
  { id: "operations", label: "Operação", icon: "🚨", items: [
    { id: "incidents",          icon: "⚠️",  label: "Incidentes" },
    { id: "intelligent-alerts", icon: "🧠",  label: "Alertas Inteligentes" },
    { id: "events-timeline",    icon: "🕐",  label: "Timeline de Eventos" },
    { id: "noc-realtime",       icon: "🖥️",  label: "NOC" },
  ]},
  { id: "aiops", label: "AIOps", icon: "🧠", items: [
    { id: "aiops",         icon: "🔮", label: "AIOps" },
    { id: "aiops-v3",      icon: "🤖", label: "AIOps v3" },
    { id: "ai-activities", icon: "✨", label: "Atividades da IA" },
    { id: "predictions",   icon: "📉", label: "Predições de Falha" },
  ]},
  { id: "observability", label: "Observabilidade", icon: "📡", items: [
    { id: "observability",    icon: "🔭", label: "Observabilidade" },
    { id: "topology",         icon: "🕸️", label: "Topologia" },
    { id: "advanced-metrics", icon: "📈", label: "Métricas Avançadas" },
  ]},
  { id: "system", label: "Sistema", icon: "🔧", items: [
    { id: "discovery",     icon: "🔍", label: "Discovery" },
    { id: "probe-nodes",   icon: "🔌", label: "Probe Nodes" },
    { id: "system-health", icon: "⚙️", label: "Saúde do Sistema" },
    { id: "maintenance",   icon: "🔧", label: "GMUD" },
    { id: "settings",      icon: "🛠️", label: "Configurações" },
  ]},
  { id: "knowledge", label: "Conhecimento", icon: "📚", items: [
    { id: "knowledge-base", icon: "📚", label: "Base de Conhecimento" },
  ]},
];

var STORAGE_KEY = "coruja_sidebar_open";

function loadOpen() {
  try {
    var s = localStorage.getItem(STORAGE_KEY);
    if (s) return JSON.parse(s);
  } catch(e) {}
  var def = {};
  CATS.forEach(function(c) { def[c.id] = true; });
  return def;
}

function Sidebar(props) {
  var currentPage = props.currentPage;
  var onNavigate = props.onNavigate;
  var collapsed = props.collapsed;
  var onToggleCollapse = props.onToggleCollapse;
  var alertCount = props.alertCount || 0;
  var user = props.user;
  var onLogout = props.onLogout;

  var openState = useState(loadOpen);
  var openCats = openState[0];
  var setOpenCats = openState[1];

  useEffect(function() {
    try { localStorage.setItem(STORAGE_KEY, JSON.stringify(openCats)); } catch(e) {}
  }, [openCats]);

  function toggleCat(id) {
    setOpenCats(function(prev) {
      var next = Object.assign({}, prev);
      next[id] = !prev[id];
      return next;
    });
  }

  var userInitial = user && user.username ? user.username[0].toUpperCase() : "U";

  return (
    React.createElement("div", { className: "sidebar" + (collapsed ? " sidebar--collapsed" : "") },

      React.createElement("div", { className: "sidebar-logo", onClick: function() { onNavigate("dashboard"); } },
        React.createElement("div", { className: "sidebar-logo-icon" }, "\uD83E\uDD89"),
        !collapsed && React.createElement("div", { className: "sidebar-logo-text" },
          React.createElement("span", { className: "sidebar-logo-name" }, "Coruja"),
          React.createElement("span", { className: "sidebar-logo-version" }, "Monitor v3")
        )
      ),

      React.createElement("nav", { className: "sidebar-nav", "aria-label": "Navegação principal" },
        CATS.map(function(cat) {
          var isOpen = openCats[cat.id];
          var hasActive = cat.items.some(function(i) { return i.id === currentPage; });

          return React.createElement("div", { key: cat.id, className: "sidebar-category" },

            !collapsed
              ? React.createElement("button", {
                  className: "sidebar-category-header" + (hasActive ? " has-active" : ""),
                  onClick: function() { toggleCat(cat.id); },
                  "aria-expanded": isOpen
                },
                React.createElement("span", { className: "sidebar-category-icon" }, cat.icon),
                React.createElement("span", { className: "sidebar-category-label" }, cat.label),
                React.createElement("span", { className: "sidebar-category-chevron" + (isOpen ? " open" : "") }, "›")
              )
              : React.createElement("div", { className: "sidebar-category-divider", title: cat.label }),

            React.createElement("div", {
              className: "sidebar-category-items" +
                (!collapsed && isOpen ? " open" : "") +
                (collapsed ? " collapsed-items" : "")
            },
              cat.items.map(function(item) {
                return React.createElement("button", {
                  key: item.id,
                  className: "sidebar-item" + (currentPage === item.id ? " active" : ""),
                  onClick: function() { onNavigate(item.id); },
                  title: collapsed ? item.label : undefined,
                  "data-tooltip": item.label
                },
                  React.createElement("span", { className: "sidebar-item-icon" }, item.icon),
                  !collapsed && React.createElement("span", { className: "sidebar-item-label" }, item.label),
                  !collapsed && item.id === "intelligent-alerts" && alertCount > 0 &&
                    React.createElement("span", { className: "sidebar-item-badge" }, alertCount > 99 ? "99+" : alertCount)
                );
              })
            )
          );
        })
      ),

      React.createElement("div", { className: "sidebar-footer" },
        user && React.createElement("div", { className: "sidebar-footer-user", title: collapsed ? (user.username || "") : undefined },
          React.createElement("div", { className: "sidebar-avatar" }, userInitial),
          !collapsed && React.createElement("div", { className: "sidebar-user-info" },
            React.createElement("div", { className: "sidebar-user-name" }, user.username),
            React.createElement("div", { className: "sidebar-user-role" }, user.role || "Operador")
          ),
          !collapsed && React.createElement("button", {
            className: "sidebar-logout-btn",
            onClick: onLogout,
            title: "Sair",
            "aria-label": "Sair"
          },
            React.createElement("svg", { width: "14", height: "14", viewBox: "0 0 24 24", fill: "none", stroke: "currentColor", strokeWidth: "2", strokeLinecap: "round", strokeLinejoin: "round" },
              React.createElement("path", { d: "M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" }),
              React.createElement("polyline", { points: "16 17 21 12 16 7" }),
              React.createElement("line", { x1: "21", y1: "12", x2: "9", y2: "12" })
            )
          )
        ),
        React.createElement("button", {
          className: "sidebar-collapse-btn",
          onClick: onToggleCollapse,
          title: collapsed ? "Expandir menu" : "Recolher menu",
          "aria-label": collapsed ? "Expandir menu" : "Recolher menu"
        },
          React.createElement("span", { className: "sidebar-collapse-icon" }, collapsed ? "▶" : "◀"),
          !collapsed && React.createElement("span", { className: "sidebar-item-label" }, "Recolher")
        )
      )
    )
  );
}

export default Sidebar;