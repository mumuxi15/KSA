import { NavLink } from 'react-router-dom';
import { IoHome, IoAnalytics } from "react-icons/io5";
import { FaSailboat } from "react-icons/fa6";
import { GrStorage } from "react-icons/gr";

import 'bootstrap/dist/css/bootstrap.css';

function Navbar() {
  const items = [
    { path: '/', title: 'Home' , icon:<IoHome />},
    { path: '/analytics', title: 'Analytics', icon:<IoAnalytics /> },
    { path: '/shipping', title: 'Shipping', icon:<FaSailboat /> },
    { path: '/inventory', title: 'Inventory', icon:<GrStorage />},
  ];

  return (
      <nav className="sidenav">
          <h3>DashBoard </h3>

          <ul className="nav flex-column mb-auto">
              {
                 items.map((item, i) => (
                <li key={i} className="nav-item  bar-item">
                  <NavLink className="nav-link active" to={item.path}>
                      {item.icon}
                      <span>{item.title}</span>
                  </NavLink>

                </li>
                ))

              }

        </ul>
    </nav>




  );
}

export default Navbar;