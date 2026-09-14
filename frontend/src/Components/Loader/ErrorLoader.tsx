// Styles
import styles from "./ErrorLoader.module.css"

interface LoaderProps {
  message?: string;
  title?: string;
}

export const ErrorLoader = (props: LoaderProps = {}) => {
  return (
    <div className={`${styles["flex-container-error"]}`}>
      <span className={styles["shake"]}>{props.title && <h1>{props.title}</h1>}</span>
      {props.message && <p>{props.message}</p>}
    </div>
  )
}

export default ErrorLoader
