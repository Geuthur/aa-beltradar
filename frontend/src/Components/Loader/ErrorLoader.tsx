// Third Party
import { TriangleAlert } from "lucide-react";

// AA Belt Radar
import styles from "@/Components/Loader/ErrorLoader.module.css";

interface LoaderProps {
  message?: string;
  title?: string;
}

export const ErrorLoader = (props: LoaderProps = {}) => {
  return (
    <div className={`${styles["flex-container-error"]}`}>
      <span className={styles["shake"]}><TriangleAlert className={styles["icon-96"]} size={96} aria-hidden="true" /></span>
      {props.title && <h3>{props.title}</h3>}
      {props.message && <p>{props.message}</p>}
    </div>
  );
};

export default ErrorLoader;