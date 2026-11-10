import { Header } from "./components/Header";
import { Landing } from "./pages/Landing";
import { Tool } from "./pages/Tool";
import { useRoute } from "./route";

export default function App() {
  const route = useRoute();
  return (
    <>
      <Header route={route} />
      <main id="contenu">{route === "analyse" ? <Tool /> : <Landing />}</main>
      <footer className="site-footer">
        <p>
          Projet de cours DevOps, Dakar Institute of Technology, Licence 3. Données météo :{" "}
          <a href="https://open-meteo.com/">Open-Meteo.com</a> (licence CC BY 4.0).
        </p>
      </footer>
    </>
  );
}
