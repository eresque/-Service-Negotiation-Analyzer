import Block from '../../components/block/Block';
import Button from '../../components/button/Button';
import home from '../../img/home.svg';
import { Link } from 'react-router-dom';
import './style.scss'

type ResultPageProps = {
    data: any
}

const ResultPage = (props: ResultPageProps): JSX.Element => {

    console.log(props.data);

    return (
        <div className="result-page">
            <h1 className="result-name">Результаты вычислений</h1>

            <div className="results">
                {props.data.map((elem: any, index: React.Key) => {
                    return (
                        <>
                            <Block className='block-res' key={index}>
                                <div className='list-dashboards'>
                                    <div className='top-dashboards'>
                                        <h2>🔍 Распознано</h2>
                                        <Block className='dashboard-1'>
                                            <h3>{elem['name']}</h3>
                                            <hr />
                                            <p className='text-file'>"{elem['text']}"</p>
                                        </Block>
                                    </div>
                                    <div className='bottom-dashboards'>
                                        <h2>❌ Ошибки</h2>
                                        <Block className='dashboard-2'>
                                            {elem['errors'].map((err: any, index: number) => {
                                                let key = index + 1;
                                                return (
                                                    <>
                                                        <h4>{key}. {err['name_error']}</h4>
                                                        <p className='text-error'>"{err['text_error']}"</p>
                                                    </>
                                                )
                                            })}
                                        </Block>
                                    </div>
                                </div>
                            </Block>
                        </>
                    )
                })}
            </div>

            <div className="help">
                <div className="help-text">
                    <h2 className="help-message">Забыли, как пользоваться? Жми сюда</h2>
                    <h6 className="emoji-right">👉</h6>
                    <h6 className="emoji-down">👇</h6>
                </div>
                <div className="home">
                    <Link to="/" className="link">
                        <Button
                            className="btn-home"
                            text="Домой">
                            <img
                                src={home}
                                alt="Дом"
                            />
                        </Button>
                    </Link>
                </div>
            </div>
        </div>
    );
};

export default ResultPage; 
