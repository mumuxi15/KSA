import React from "react";
import Shipping from "../pages/shipping";
import Color from "../pages/color";
import Home from "../pages/dashboard";
import Icon from "@mui/material/Icon";
//import { NavLink } from 'react-router-dom'

const routes = [
  {
    path: "/",
    key: "ROOT",
    exact: true,
    sidebar: "Home",
    breadcrumbName: "Home",
    icon: <Icon>home</Icon>,
    component: Home,
  },

  {
    path: "/color",
    key: "COLOR",
    sidebar: "Color",
    breadcrumbName: "Color",
    icon: <Icon>palette</Icon>,
    component: Color,
  },

  {
      path: "/shipping",
    key: "SHIPPING",
    sidebar: "Shipping",
    breadcrumbName: "Shipping",
    icon: <Icon>insert_chart</Icon>,
    component: Shipping,


  }
];

export default routes;
