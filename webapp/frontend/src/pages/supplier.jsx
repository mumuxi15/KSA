import axios from "axios";
import { useState, useEffect } from "react";

axios.defaults.baseURL = 'http://localhost:8000';

export function Supplier(){
    const [suppliers, setSuppliers] = useState([]);

  useEffect(() => {
    async function getAllSupplier() {
      try {
        const suppliers = await axios.get("/supplier/");
        setSuppliers(suppliers.data);
      } catch (error) {
        console.log(error);
      }
    }
    getAllSupplier();
  }, []);

  return (
    <div className="container">
      <header>
        <h1>Supplier Page </h1>
      </header>
      <table>
        <thead>
          <tr>
            <th>Code</th>
            <th>Name</th>
            <th>Email</th>
          </tr>
        </thead>
        <tbody>
          {suppliers.map((student, i) => (
            <tr key={i}>
              <td>{student.supplier}</td>
              <td>{student.supplier_name}</td>
              <td>{student.email}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );

    }