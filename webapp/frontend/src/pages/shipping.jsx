import { useState, useEffect } from "react";
import { Outlet, useParams, useNavigate } from 'react-router-dom';
import axios from "axios";
import React from 'react';
import Container from 'react-bootstrap/Container';
import 'bootstrap/dist/css/bootstrap.css';
import './custom.css'

const drawerWidth = 240;

axios.defaults.baseURL = 'http://localhost:8000';


function Shipping(){
    const [inv, setInv] = useState([]);
    const [groupedData, setGroupedData] = useState({});

    useEffect(() => {
        axios.get('/shipping/raw')
            .then(response => {
                setInv(response.data);
                groupBy(response.data);

          })
            .catch(error => {
                console.error('There was an error fetching the data!', error);
          });
      }, []);




    const handleRowClick = (supplr) => {
        console.log("hello");
    };
    const groupBy = (data) => {
        const grouped = data.reduce((acc, curr) => {
//             console.log(acc);
            const supplr = curr.supplr;
            if (!acc[supplr]) {
                console.log('---------  create --------------', supplr);
                acc[supplr] = {
                    supplr: curr.supplr,
                    condat: curr.condat,
                    late: curr.late,
                };
            }
            console.log('output ',acc[supplr].condat, '  curr:',curr.condat);
            acc[supplr].condat = acc[supplr].condat < curr.condat ? acc[supplr].condat : curr.condat;
//             console.log('supplr = ',supplr,'acc: ',output[supplr].condat,'curr ',curr.condat);
            acc[supplr].late += curr.late;     // Aggregate sum for 'late'
            return acc;
        }, {});

        setGroupedData(Object.values(grouped));
        console.log('grouped Data : ',Object.values(grouped));
    }



  return (

    <div className="right-section">
    <h1 className="table-title"> SHIPPING SUMMARY</h1>
    <table className="table table-striped">
        <thead>
            <tr>
                <th>SUPPLR</th>
                <th>CONDAT</th>
                <th>LATE</th>
                <th>ATTENTION</th>
                <th>Z items</th>
            </tr>
        </thead>
    <tbody>
        {Object.keys(groupedData).map((item, index) => (
            <tr key={index}>
              <td className="hovercolor"></td>
              <td>{item}</td>
            </tr>
          ))}

    </tbody>
    </table>
    </div>

  );
}

export default Shipping